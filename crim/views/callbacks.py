from django.shortcuts import render
import json

from django.http import HttpResponse
from django.conf import settings
from django.core.paginator import EmptyPage, InvalidPage
from django.contrib.auth.decorators import login_required
from crim.helpers.solrsearch import CRIMSolrSearch

from crim.models.piece import CRIMPiece
# from crim.models.observation import CRIMObservation
# from crim.models.relationship import CRIMRelationship


class JsonResponse(HttpResponse):
    def __init__(self, content, content_type='application/json', status=None):
        super(JsonResponse, self).__init__(
            content=json.dumps(content),
            status=status,
            content_type=content_type
        )


# Could add favorites here if logged in; see Du Chemin

def result_callback(request, restype):
    if restype == 'piece':
        return _fetch_piece_results(request)
    elif restype == 'relationship':
        return _fetch_relationship_results(request)
    elif restype == 'facet':
        return _fetch_facet_results(request)


def _fetch_piece_results(request):
    s = CRIMSolrSearch(request)
    piece_res = s.group_search(['title'], fq=['type:(crim_piece OR crim_relationship)'])

    if piece_res.count == 0:
        return render(request, 'search/no_results.html')

    try:
        wpage = int(request.GET.get('wpage', '1'))
    except ValueError:
        wpage = 1

    try:
        piece_results = piece_res.page(wpage)
    except (EmptyPage, InvalidPage):
        piece_results = piece_res.page(piece_res.num_pages)
    piece_results.pager_id = 'pieces'

    is_logged_in = False
    if request.user.is_authenticated():
        is_logged_in = True
#         profile = request.user.profile
#         favorite_pieces = [f[0] for f in profile.favorited_piece.all().values_list('piece_id')]
#         print favorite_pieces
#         if favorite_pieces:
#             for piece in piece_results.object_list:
#                 if piece.piece_id in favorite_pieces:
#                     piece.is_favorite = True
#                 else:
#                     piece.is_favorite = False

    data = {
        'piece_results': piece_results,
        'is_logged_in': is_logged_in,
    }
    return render(request, 'search/piece_result_list.html', data)


def _fetch_relationship_results(request):
    s = CRIMSolrSearch(request)
    el_res = s.search(fq=['type:crim_relationship'], sort=['piece_id asc', 'phrase_number asc', 'start_measure asc'])

    if el_res.count == 0:
        return render(request, 'search/no_results.html')

    try:
        epage = int(request.GET.get('epage', '1'))
    except ValueError:
        epage = 1

    try:
        relationship_results = el_res.page(epage)
    except (EmptyPage, InvalidPage):
        relationship_results = el_res.page(el_res.num_pages)
    relationship_results.pager_id = 'relationships'

    data = {
        'relationship_results': relationship_results
    }
    return render(request, 'search/relationship_result_list.html', data)


def _fetch_facet_results(request):
    s = CRIMSolrSearch(request)
    facet_params = {
        'facet_mincount': 1,
    }
    facet_res = s.facets(fq=['type:crim_relationship'], **facet_params)
    facets = facet_res.facet_counts['facet_fields']
    # filtered_facets = dict([(k, v) for k, v in facets.items() if k in settings.DISPLAY_FACETS])

    filtered_facets = []
    for k, v in facets.items():
        this_facet = []
        if k not in settings.DISPLAY_FACETS.keys():
            continue
        for facet_value, num in v.items():
            if k == "book_id_title":
                facet_info = facet_value.split("_")
                this_facet.append([facet_info[1], settings.DISPLAY_FACETS[k][0], facet_info[0]])
            else:
                this_facet.append([facet_value, settings.DISPLAY_FACETS[k][0]])

        this_facet.sort()
        filtered_facets.append([settings.DISPLAY_FACETS[k][1], this_facet])

    filtered_facets.sort()

    data = {
        'facet_results': filtered_facets,
    }
    return render(request, 'search/facets.html', data)
