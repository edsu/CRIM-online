from django.shortcuts import render
from crim.helpers.solrsearch import CRIMSolrSearch


def search(request):
    if 'q' not in request.GET:
        return _empty_search(request)
    else:
        return render(request, 'search/results.html')


def _empty_search(request):
    # I believe this is meant to return all possible results. See Du Chemin implementation.
    s = CRIMSolrSearch(request)
    ret = s.facets(fq=['crim_piece'], rows=0)

    facets = ret.facet_counts['facet_fields']
    people = sorted(facets['people'])

    data = {
        'people': people,
    }
    return render(request, 'search/search.html', data)


def __construct_voice_facet(voice, group, hidden=True):
    d = {
        'id': "{0}_{1}".format(voice.lower(), group),
        'voice': voice,
        'group': group,
        'hidden': hidden,
        'checked': False
    }
    if voice == "None":
        d['checked'] = True

    return VoiceFacet(**d)


class VoiceFacet(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)
