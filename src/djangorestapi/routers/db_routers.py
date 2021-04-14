class Django_Auth_Router: # auth_db
    def __init__(self):
        self.router_app_lables = {'admin', 'auth', 'contenttypes', 'sessions', 'messages'}

    def db_for_read(self, model, **hints):
        if(model._meta.app_label in self.router_app_lables):
            return 'auth_db'
        else:
            return None
    
    def db_for_write(self, model, **hints):
        if(model._meta.app_label in self.router_app_lables):
            return 'auth_db'
        else:
            return None
    
    def allow_realtion(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.router_app_lables
        or obj2._meta.app_label in self.router_app_lables):
            return True
        else:
            return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if(app_label in self.router_app_lables):
            return db == 'auth_db'
        else:
            return None

class App_Router: # app_db
    def __init__(self):
        self.router_app_lables = {
            'auth_prime', 'content_delivery', 'analytics', 'user_personal'
        }

    def db_for_read(self, model, **hints):
        if(model._meta.app_label in self.router_app_lables):
            return 'app_db'
        else:
            return None
    
    def db_for_write(self, model, **hints):
        if(model._meta.app_label in self.router_app_lables):
            return 'app_db'
        else:
            return None
    
    def allow_realtion(self, obj1, obj2, **hints):
        if( obj1._meta.app_label in self.router_app_lables
        or obj2._meta.app_label in self.router_app_lables):
            return True
        else:
            return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if(app_label in self.router_app_lables):
            return db == 'app_db'
        else:
            return None
    