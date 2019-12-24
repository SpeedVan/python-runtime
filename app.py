#!/usr/bin/env python

import multiprocessing

import gunicorn.app.base

import app_pre_process

import os

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    options = {
        'bind': '%s:%s' % ('0.0.0.0', os.getenv("PROXY_PORT", '8888')),
        'workers': 8,
        'threads': 1,
        'timeout': 30,
        'debug': True,
        'backlog': 2048
    }
    StandaloneApplication(app_pre_process.app, options).run()