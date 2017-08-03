from django.contrib.postgres.search import SearchRank, SearchQuery
from django.db.models import F, Q

from regcore.models import Document
from regcore.responses import success
from regcore_read.views.search_utils import requires_search_args, PAGE_SIZE


@requires_search_args
def search(request, doc_type, search_args):
    sections_query = Document.objects\
        .annotate(rank=SearchRank(
            F('documentindex__search_vector'), SearchQuery(search_args.q)))\
        .filter(rank__gte=0.15)\
        .order_by('-rank')

    if search_args.version:
        sections_query = sections_query.filter(version=search_args.version)
    # can't filter regulation yet
    start = search_args.page * PAGE_SIZE
    end = start + PAGE_SIZE

    return success({
        'total_hits': sections_query.count(),
        'results': transform_results(sections_query[start:end], search_args.q),
    })


def transform_results(sections, search_terms):
    """Convert matching Section objects into the corresponding dict for
    serialization."""
    final_results = []
    for section in sections:
        first_match = section.get_descendants(include_self=True)\
            .filter(Q(text__search=search_terms) |
                    Q(title__search=search_terms))\
            .first()

        final_results.append({
            'text': first_match.text,
            'label': first_match.label_string.split('-'),
            'version': first_match.version,
            'regulation': first_match.label_string.split('-')[0],
            'label_string': first_match.label_string,
            'title': section.title,
        })
    return final_results
