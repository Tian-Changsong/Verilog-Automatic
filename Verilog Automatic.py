import sublime
import sublime_plugin
import re
import os
import ctagsplugin
import time


def get_match(pattern, string, group_number):
    compiled_pattern = re.compile(pattern)
    match = re.match(compiled_pattern, string)
    return match.group(group_number)


def get_list(text_command, pattern, group_number):
    match_list = []
    regions = text_command.view.find_all(pattern)
    for region in regions:
        line_string = text_command.view.substr(region)
        match_substring = get_match(pattern, line_string, group_number)
        match_list.append(match_substring)
    return match_list


def find_insert_region(text_command, insert_pattern, insert_mark, search_start):
    insert_region = text_command.view.find(insert_pattern, search_start)
    if insert_region is None:
        sublime.status_message('Can not find the "'+insert_mark+'" mark !')
        raise Exception('Can not find the "'+insert_mark+'" mark !')
    return insert_region


def check_file_ext(file_name):
    ext_name = os.path.splitext(file_name)[1]
    if ext_name != '.v' and ext_name != '.V':
        sublime.status_message('This file "'+file_name+'" is not a verilog file !')
        raise Exception('This file "'+file_name+'" is not a verilog file !')


class AutoDefCommand(sublime_plugin.TextCommand):

    """auto add wire declaration for instances to connect"""

    def run(self, edit):
        file_name = self.view.file_name()
        check_file_ext(file_name)
        undefined_instance_port_dict = {}
        insert_pattern = r"/\*\bautodef\b\*/"
        insert_mark = "/*autodef*/"
        insert_region = find_insert_region(self, insert_pattern, insert_mark, 0)
        insert_point = insert_region.end()
        search_defined_pattern = r'^\s*(?:\b(?:input|wire|reg)\b)\s*(?:\[\S+\s*:\s*\S+\])*\s*(\w+)'
        search_instance_pattern = r'^\s*(?:[.]\w+\s*\(\s*)(\w+)\s*(\[\s*\w+\s*[:]\s*\w+\s*\])*\)'
        instance_port_name_list = get_list(self, search_instance_pattern, 1)
        instance_port_bitwidth_list = get_list(self, search_instance_pattern, 2)
        list_length = len(instance_port_name_list)
        defined_list = get_list(self, search_defined_pattern, 1)
        for i in range(list_length):
            if instance_port_name_list[i] in defined_list:
                continue
            else:
                undefined_instance_port_dict[instance_port_name_list[i]] = instance_port_bitwidth_list[i]
        for key in undefined_instance_port_dict.keys():
            insert_content = "\n//assign "+key+"="
            self.view.insert(edit, insert_point, insert_content)
        for key in undefined_instance_port_dict.keys():
            if undefined_instance_port_dict[key] is not None:
                insert_content = "\nwire "+undefined_instance_port_dict[key]+key+";"
            else:
                insert_content = "\nwire "+key+";"
            self.view.insert(edit, insert_point, insert_content)
        sublime.status_message("Instance port-connections successfully generated !")


class AutoPortCommand(sublime_plugin.TextCommand):

    """auto add module port to the current verilog module"""

    def insert_list(self, edit, list_to_insert, insert_point):
        range_list = range(len(list_to_insert))
        range_list.reverse()
        for i in range_list:
            self.view.insert(edit, insert_point, list_to_insert[i])
            self.view.insert(edit, insert_point, '\t\t\t')
            if i != 0:
                self.view.insert(edit, insert_point, ',\n')
            else:
                self.view.insert(edit, insert_point, '\n')

    def run(self, edit):
        file_name = self.view.file_name()
        check_file_ext(file_name)
        input_pattern = r'^\s*(?:\binput\b)\s*(\[\S+\s*:\s*\S+\])*\s*(\w+)'
        output_pattern = r'^\s*(?:\boutput\b)\s*(\[\S+\s*:\s*\S+\])*\s*(\w+)'
        inout_pattern = r'^\s*(?:\binout\b)\s*(\[\S+\s*:\s*\S+\])*\s*(\w+)'
        insert_pattern = r"((?<=/\*\bautoport\b\*/)[\d\D]*?(?=\);))"
        insert_mark = r"/*autoport*/"
        insert_region = find_insert_region(self, insert_pattern, insert_mark, 0)
        insert_point = insert_region.begin()
        self.view.erase(edit, insert_region)
        input_list = get_list(self, input_pattern, 2)
        output_list = get_list(self, output_pattern, 2)
        inout_list = get_list(self, inout_pattern, 2)
        if len(input_list) > 0:
            self.insert_list(edit, input_list, insert_point)
            self.view.insert(edit, insert_point, "\n//input")
        if len(output_list) > 0:
            if len(input_list) > 0:
                self.view.insert(edit, insert_point, ",")
            self.insert_list(edit, output_list, insert_point)
            self.view.insert(edit, insert_point, "\n//output")
        if len(inout_list) > 0:
            if len(input_list) > 0 or len(output_list) > 0:
                self.view.insert(edit, insert_point, ",")
            self.insert_list(edit, inout_list, insert_point)
            self.view.insert(edit, insert_point, "\n//inout")
        sublime.status_message("Module ports successfully generated !")


class AutoInstCommand(sublime_plugin.TextCommand):

    """auto generate instance"""

    def get_module_file_handle(self, module_to_find, tag_handle, tag_file):
        found_module_flag = 0
        search_pattern = r"^[\d\D]*\bmodule\b\s*"+module_to_find+r"\b"
        compiled_search_pattern = re.compile(search_pattern)
        replaced_line = ''
        for line in tag_handle:
            if re.match(compiled_search_pattern, line):
                replaced_line = line.replace('\\', '/')
                found_module_flag = 1
                break
        if not found_module_flag:
            sublime.status_message('Can not find module "'+module_to_find+'" in the tag file !')
            raise Exception('Can not find module "'+module_to_find+'" in the tag file !')
        capture_module_file_pattern = r"^(?:\w+\s*)(\S+)"
        module_file_path = re.match(capture_module_file_pattern, replaced_line).group(1)
        tag_dirname = os.path.dirname(tag_file)
        module_file_os_path = os.path.normpath(module_file_path)
        module_file_os_name = os.path.join(tag_dirname, module_file_os_path)
        try:
            module_file_handle = open(module_file_os_name)
            return module_file_handle
        except IOError:
            sublime.status_message('Can not find module "'+module_to_find+'", the definition file does not exist !')
            raise Exception('Can not find module "'+module_to_find+'", the definition file does not exist !')

    def check_file_ext(self, file_name):
        ext_name = os.path.splitext(file_name)[1]
        if ext_name != '.v' and ext_name != '.V':
            sublime.status_message('This file "'+file_name+'" is not a verilog file !')
            raise Exception('This file "'+file_name+'" is not a verilog file !')

    def get_module_name(self, region):
        word_region = self.view.word(region.begin())
        module_name = self.view.substr(word_region)
        # check the module name if valid
        if re.match('\w+', module_name) is None:
            sublime.status_message("Invalid module name '"+module_name+"' selected !")
            raise Exception("Invalid module name '"+module_name+"' selected !")
        else:
            return module_name
    # def find_module_in_tag(self):

    def find_tag(self, file_name):
        tag_file = ctagsplugin.find_tags_relative_to(file_name)
        if tag_file:
            return tag_file
        else:
            sublime.status_message("Can not find any tag file ! Please generate the tag file using Ctags !")
            raise Exception('Can not find any tag file ! Please generate the tag file using Ctags !')

    def get_list(self, pattern, file_handle, group_number, module_name):
        match_list = []
        scope_valid = 0
        compiled_pattern = re.compile(pattern)
        file_handle.seek(0)
        module_scope_start_compiled_pattern = re.compile(r"^\s*\bmodule\b\s*\b"+module_name+r"\b")
        module_scope_end_compiled_pattern = re.compile(r"^\s*\bendmodule\b")
        for line in file_handle:
            module_scope_begin_match = re.match(module_scope_start_compiled_pattern, line)
            module_scope_end_match = re.match(module_scope_end_compiled_pattern, line)
            match = re.match(compiled_pattern, line)
            if module_scope_begin_match:
                scope_valid = 1
            elif module_scope_end_match and scope_valid:
                scope_valid = 0
                break
            if match and scope_valid:
                match_list.append(match.group(group_number))
        return match_list

    def insert_list(self, edit, name_list_to_insert, bitwidth_list_to_insert, insert_point):
        range_list = range(len(name_list_to_insert))
        range_list.reverse()
        for i in range_list:
            if bitwidth_list_to_insert[i] is not None:
                self.view.insert(edit, insert_point, '.'+name_list_to_insert[
                                 i]+'('+name_list_to_insert[i]+bitwidth_list_to_insert[i]+')')
            else:
                self.view.insert(edit, insert_point, '.'+name_list_to_insert[i]+'('+name_list_to_insert[i]+')')
            self.view.insert(edit, insert_point, '\t\t\t')
            if i != 0:
                self.view.insert(edit, insert_point, ',\n')
            else:
                self.view.insert(edit, insert_point, '\n')

    def run(self, edit):
        file_name = self.view.file_name()
        check_file_ext(file_name)
        self.find_tag(file_name)
        for region in self.view.sel():
            module_to_find = self.get_module_name(region)
            tag_file = self.find_tag(file_name)
            tag_handle = open(tag_file)
            module_file_handle = self.get_module_file_handle(module_to_find, tag_handle, tag_file)
            input_pattern = r'^\s*(?:\binput\b)\s*(\[\S+\s*:\s*\S+\])*\s*(\w+)'
            output_pattern = r'^\s*(?:\boutput\b)\s*(\[\S+\s*:\s*\S+\])*\s*(\w+)'
            inout_pattern = r'^\s*(?:\binout\b)\s*(\[\S+\s*:\s*\S+\])*\s*(\w+)'
            insert_pattern = r"((?<=/\*\bautoinst\b\*/)[\d\D]*?(?=\);))"
            insert_mark = r"/*autoinst*/"
            input_name_list = self.get_list(input_pattern, module_file_handle, 2, module_to_find)
            input_bitwidth_list = self.get_list(input_pattern, module_file_handle, 1, module_to_find)
            output_name_list = self.get_list(output_pattern, module_file_handle, 2, module_to_find)
            output_bitwidth_list = self.get_list(output_pattern, module_file_handle, 1, module_to_find)
            inout_name_list = self.get_list(inout_pattern, module_file_handle, 2, module_to_find)
            inout_bitwidth_list = self.get_list(inout_pattern, module_file_handle, 1, module_to_find)
            insert_region = find_insert_region(self, insert_pattern, insert_mark, region.begin())
            insert_point = insert_region.begin()
            self.view.erase(edit, insert_region)

            if len(input_name_list) > 0:
                self.insert_list(edit, input_name_list, input_bitwidth_list, insert_point)
            if len(output_name_list) > 0:
                if len(input_name_list) > 0:
                    self.view.insert(edit, insert_point, ",")
                self.insert_list(edit, output_name_list, output_bitwidth_list, insert_point)
            if len(inout_name_list) > 0:
                if len(input_name_list) > 0 or len(output_name_list) > 0:
                    self.view.insert(edit, insert_point, ",")
                self.insert_list(edit, inout_name_list, inout_bitwidth_list, insert_point)
            sublime.status_message("Instance successfully generated!")
            tag_handle.close()
            module_file_handle.close()


class AddHeaderCommand(sublime_plugin.TextCommand):

    """add file header for verilog code"""

    def run(self, edit):
        file_name = self.view.file_name()
        check_file_ext(file_name)
        file_name_without_path = os.path.split(file_name)[1]
        plugin_settings = sublime.load_settings("Verilog Automatic.sublime-settings")
        author = plugin_settings.get("Author")
        company = plugin_settings.get("Company")
        email = plugin_settings.get("Email")
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.view.insert(edit, 0, "\n//"+"="*98+"\n")
        self.view.insert(edit, 0, "\n//")
        self.view.insert(edit, 0, "\n//")
        self.view.insert(edit, 0, "\n//  Description"+" "*3+": ")
        self.view.insert(edit, 0, "\n//")
        if email:
            self.view.insert(edit, 0, "\n//  Email"+" "*9+": "+email)
        if company:
            self.view.insert(edit, 0, "\n//  Company"+" "*7+": "+company)
        if author:
            self.view.insert(edit, 0, "\n//  Author"+" "*8+": "+author)
        self.view.insert(edit, 0, "\n//  Revision"+" "*6+": ")
        self.view.insert(edit, 0, "\n//  Last Modified : ")
        self.view.insert(edit, 0, "\n//  Created On"+" "*4+": "+current_time)
        self.view.insert(edit, 0, "\n//  Filename"+" "*6+": "+file_name_without_path)
        self.view.insert(edit, 0, "//"+"="*98)
        sublime.status_message("File header successfully added !")


class ChangeModifyTimeCommand(sublime_plugin.TextCommand):

    """change the last modified time"""

    def run(self, edit):
        modify_time_pattern = r"(?<=^//  Last Modified : )[\d\D]*?$"
        insert_region = self.view.find(modify_time_pattern, 0)
        if insert_region is None:
            return
        else:
            insert_point = insert_region.begin()
            self.view.erase(edit, insert_region)
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            self.view.insert(edit, insert_point, current_time)


class LastModifyListener(sublime_plugin.EventListener):

    def on_pre_save(self, view):
        if 'Verilog' in view.settings().get('syntax') and view.is_dirty():
            view.run_command("change_modify_time")
