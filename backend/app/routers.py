class DefaultRouter:
    def db_for_read(self, model, **hints):
        return 'user' if model._meta.app_label == 'accounts' else 'default'

    def db_for_write(self, model, **hints):
        return 'user' if model._meta.app_label == 'accounts' else 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # MSA 완전 분리상황에서 각각의 프로젝트가 마이그레이션을 담당할 때
        # return app_label != 'accounts'

        # accounts 모듈이 마이그레이션 되지만 사용되지 않는다.
        return True
