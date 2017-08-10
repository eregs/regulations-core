from model_mommy.recipe import Recipe

from regcore.models import Document


# Account for mptt-related edge case
doc_recipe = Recipe(Document, lft=None, rght=None, tree_id=None,
                    _fill_optional=['title'])
