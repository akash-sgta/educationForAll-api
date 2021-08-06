## ================================================================================================= ##
# App realted items


class App:  # app
    def __init__(self):
        self.router_app_lables = {"iam"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.router_app_lables:
            return "app"
        else:
            return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.router_app_lables:
            return "app"
        else:
            return None

    def allow_realtion(self, obj1, obj2, **hints):
        if obj1._meta.app_label in self.router_app_lables or obj2._meta.app_label in self.router_app_lables:
            return True
        else:
            return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.router_app_lables:
            return db == "app"
        else:
            return None


## ================================================================================================= ##
# Django realted items


class Django_Auth:  # django
    def __init__(self):
        self.router_app_lables = {"admin", "auth", "contenttypes", "sessions", "messages"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.router_app_lables:
            return "django"
        else:
            return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.router_app_lables:
            return "django"
        else:
            return None

    def allow_realtion(self, obj1, obj2, **hints):
        if obj1._meta.app_label in self.router_app_lables or obj2._meta.app_label in self.router_app_lables:
            return True
        else:
            return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.router_app_lables:
            return db == "django"
        else:
            return None
