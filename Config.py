import os
import configparser
import errno

class Config:
    midi_path = None
    dorico_pj_path = None
    prefix_ignore_dorico = None
    suffix = None
    dorico_exe_path = None
    
    def __init__(self, ini_path):
        config = configparser.ConfigParser()
        config.read(ini_path, 'UTF-8')
        
        # パラメータ
        self.midi_path = config.get('info', 'midi_path')
        self.dorico_pj_path = config.get('info', 'dorico_pj_path')
        self.dorico_exe_path = config.get('info', 'dorico_exe_path')
        self.prefix_ignore_dorico = config.get('info', 'prefix_ignore_dorico')
        
        # パラメータチェック
        if not os.path.isdir(self.midi_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.midi_path)
        
        if not os.path.isdir(self.dorico_pj_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.dorico_pj_path)

        if not os.path.isfile(self.dorico_exe_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.dorico_exe_path)
