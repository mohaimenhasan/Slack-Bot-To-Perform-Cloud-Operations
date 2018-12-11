import os
import sys
import json
import logging
import inspect
import importlib
import types
import threading
import pprint

from types import ModuleType


def create_skill(json_file):
    def populate_skill(dct):
        skill = Skill(description_file=json_file)

        try:
            if 'name' in dct:
                skill.name = dct['name']
            if 'description' in dct:
                skill.description = dct['description']
            if 'version' in dct:
                skill.version = dct['version']
            if 'invoke' in dct:
                skill.invoke = dct['invoke']
            if 'admin' in dct:
                skill.admin = dct['admin']
        except Exception as ex:
            logging.exception(ex)

        return skill

    return json.load(open(json_file), object_hook=populate_skill)

 
class Skill:
    def __init__(self, description_file=None, name=None, description=None, version=None, invoke=None, admin=False):
        self._description_file = description_file
        self._name = name
        self._description = description
        self._version = version
        self._invoke = invoke
        self._admin = admin
        self._invoke_function = None
        self._module_name = None

    def __call__(self, *args, **kwargs):
        logging.debug('Calling skill [%s] with args=%s andf kwargs=%s', self.name, args, kwargs)
        thread = threading.Thread(target=self._invoke_function, args=args, kwargs=kwargs, daemon=True)
        thread.start()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def invoke(self):
        return self._invoke

    @invoke.setter
    def invoke(self, value):
        self._invoke = value
        skill = self._import_skill(value)
        self._module_name = skill.__name__
        sys.modules[self._module_name] = skill

        for m in inspect.getmembers(skill):
            attr = getattr(skill, m[0])
            if callable(attr) and attr.__name__ == 'invoke':
                logging.debug('invoke function found: %s', attr)
                self._invoke_function = attr

    @property
    def admin(self):
        return self._admin

    @admin.setter
    def admin(self, value):
        self._admin = value

    def __str__(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)

    def reload_skill(self, skills_dir):
        self._reload_skill_recursively([sys.modules[self._module_name]], set(), skills_dir)

    def _reload_skill_recursively(self, objects, visited, skills_dir):
        """
        Recursively reload modules that this skill depends on
        """
        for o in objects:
            if type(o) is types.ModuleType and o not in visited:
                try:
                    if '__file__' in dir(o) and skills_dir in o.__file__:
                        logging.debug("Reloading module: %s, file=%s, skills_dir=%s", o, o.__file__, skills_dir)
                        importlib.reload(o)
                except Exception as ex:
                    logging.exception(ex)

                visited.add(o)
                self._reload_skill_recursively(o.__dict__.values(), visited, skills_dir)

    def _import_skill(self, module_name):
        module_name_without_ext = os.path.splitext(module_name)[0]
        module_path = os.path.dirname(self._description_file) + '/' + module_name
        sys.path.append(os.path.dirname(self._description_file))
        logging.debug('Importing skill: name=%s, path=%s', module_name_without_ext, module_path)
        loader = importlib.machinery.SourceFileLoader(module_name_without_ext, module_path)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        return mod