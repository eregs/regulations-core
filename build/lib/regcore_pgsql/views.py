from django.conf import settings
from django.contrib.postgres.search import SearchRank, SearchQuery
from django.db.models import F, Q

from regcore.models import Document
from regcore.responses import success
from regcore_read.views.search_utils import requires_search_args


def matching_sections(search_args):
    """Retrieve all Document sections that match the parsed search args."""
    sections_query = Document.objects\
        .annotate(rank=SearchRank(
            F('documentindex__search_vector'), SearchQuery(search_args.q)))\
        .filter(rank__gt=settings.PG_SEARCH_RANK_CUTOFF)\
        .order_by('-rank')

    if search_args.version:
        sections_query = sections_query.filter(version=search_args.version)
    if search_args.regulation:
        sections_query = sections_query.filter(
            documentindex__doc_root=search_args.regulation)
    # can't filter regulation yet
    return sections_query


@requires_search_args
def search(request, doc_type, search_args):
    sections = matching_sections(search_args)
    start = search_args.page * search_args.page_size
    end = start + search_args.page_size

    return success({
        'total_hits': sections.count(),
        'results': transform_results(sections[start:end], search_args.q),
    })


def transform_results(sections, search_terms):
    """Convert matching Section objects into the corresponding dict for
    serialization."""
    final_results = []
    for section in sections:
        # TODO: n+1 problem; hypothetically these could all be performed via
        # subqueries and annotated on the sections queryset
        match_node = section.get_descendants(include_self=True)\
            .filter(Q(text__search=search_terms) |
                    Q(title__search=search_terms))\
            .first() or section
        text_node = match_node.get_descendants(include_self=True)\
            .exclude(text='')\
            .first()

        final_results.append({
            'text': text_node.text if text_node else '',
            'label': match_node.label_string.split('-'),
            'version': section.version,
            'regulation': section.label_string.split('-')[0],
            'label_string': match_node.label_string,
            'match_title': match_node.title,
            'paragraph_title': text_node.title if text_node else '',
            'section_title': section.title,
            'title': section.title,
        })
    return final_results
