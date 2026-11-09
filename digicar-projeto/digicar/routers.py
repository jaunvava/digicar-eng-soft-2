"""Roteia apps explicitamente associados a aliases relacionais."""
from django.conf import settings


class AppDatabaseRouter:
    """Usa DATABASE_APP_ROUTES, por exemplo {"relatorios": "db2"}."""

    @staticmethod
    def _alias(model):
        return getattr(settings, "DATABASE_APP_ROUTES", {}).get(model._meta.app_label)

    def db_for_read(self, model, **hints):
        return self._alias(model)

    def db_for_write(self, model, **hints):
        return self._alias(model)

    def allow_relation(self, obj1, obj2, **hints):
        alias1, alias2 = self._alias(obj1), self._alias(obj2)
        if alias1 or alias2:
            return (alias1 or "default") == (alias2 or "default")
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        alias = getattr(settings, "DATABASE_APP_ROUTES", {}).get(app_label)
        if alias:
            return db == alias
        return db == "default"
