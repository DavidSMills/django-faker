"""
Django-faker uses a generator (eg faker) to generate test data for Django models and templates.
"""

__version__ = "0.2.1"


class DjangoFaker(object):

    instance = None
    populators = {}
    generators = {}

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(DjangoFaker, cls).__new__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        pass

    @staticmethod
    def get_codename(locale=None, providers=None, seed=None):
        """
        codename = locale[-Provider]*
        """
        from django.conf import settings
        # language
        locale = locale or getattr(settings, 'FAKER_LOCALE', getattr(settings, 'LANGUAGE_CODE', None))
        # providers
        providers = providers or getattr(settings, 'FAKER_PROVIDERS', None)

        codename = locale or 'default'

        if providers:
            codename += "-" + "-".join(sorted(providers))

        if seed is not None:
            codename += "-" + str(seed)

        return codename

    @classmethod
    def get_generator(cls, locale=None, providers=None, codename=None, seed=None):
        """
        use a codename to cache generators
        """

        codename = codename or cls.get_codename(locale, providers, seed)

        # Refresh if seed given
        if codename not in cls.generators or seed is not None:
            # initialize with faker.generator.Generator instance
            # and remember in cache
            from faker import Faker as FakerGenerator
            cls.generators[codename] = FakerGenerator(locale, providers)
            if seed is None:
                seed = cls.generators[codename].random_int()
            cls.generators[codename].seed(seed)

        return cls.generators[codename]

    @classmethod
    def get_populator(cls, locale=None, providers=None, seed=None):
        """

        uses:

            from django_faker import DjangoFaker
            pop = DjangoFaker.get_populator()

            from myapp import models
            pop.add_entity(models.MyModel, 10)
            pop.add_entity(models.MyOtherModel, 10)
            pop.execute()

            pop = Faker.get_populator('it_IT')

            pop.add_entity(models.MyModel, 10)
            pop.add_entity(models.MyOtherModel, 10)
            pop.execute()

        """

        codename = cls.get_codename(locale, providers, seed)

        # Refresh if seed given
        if codename not in cls.populators or seed is not None:
            generator = cls.generators.get(codename, None) or cls.get_generator(codename=codename, seed=seed)

            from .populator import Populator
            cls.populators[codename] = Populator(generator)

        return cls.populators[codename]
