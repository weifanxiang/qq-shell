import subprocess
import yaml
import os.path


class Command:
    def __init__(self, msg, config):
        self.config = config
        self.command = msg[5:]
        self.run()

    def run(self):
        if (self.command.startswith('pwd')):
            self.ret = self.config['bot']['feedback']['execute_the_command_pwd'].format(
                pwd=os.getcwd())
        elif self.command.startswith('cd '):
            self.command = self.command[3:]
            os.chdir(self.command)
            self.ret = self.config['bot']['feedback']['execute_the_command_cd'].format(
                pwd=os.getcwd())
        else:
            ret = subprocess.Popen(self.command, shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ret.wait(self.config['bot']['timeout'])
            if (ret.poll() == 1):
                # print(False, ret.stdout.read(), ret.stderr.read())
                self.result = False, ret.stderr.read().decode('gbk')
            elif (ret.poll() == 0):
                # print(True, ret.stdout.read())
                self.result = True, ret.stdout.read().decode('gbk')
            else:
                ret.terminate()
                self.result = False, False
            self.create_msg()

    def create_msg(self):
        if self.result[0]:
            template = self.config['bot']['feedback']['command_executed_successfully'].replace(
                '/hh', '\r\n')
            self.ret = template.format(out=self.result[1])
        else:
            if self.result[1]:
                template = self.config['bot']['feedback']['command_execution_failed'].replace(
                    '/hh', '\r\n')
                self.ret = template.format(err=self.result[1])
            else:
                template = self.config['bot']['feedback']['command_timeout'].replace(
                    '/hh', '\r\n')
                self.ret = template

    def __str__(self):
        return self.ret
    __repr__ = __str__
