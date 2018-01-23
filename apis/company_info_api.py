from django.http import HttpResponse, Http404

import urllib.request

# Self-written api to pull company write-up from Reuters
def get_company_info(request, symbol=''):
    if symbol != '':
        reuter_link = 'https://www.reuters.com/finance/stocks/company-profile/' + symbol + '.O'
        try:
            contents = urllib.request.urlopen(reuter_link).read().decode('utf_8')
            description_link = 'Full Description</a>'
            i0 = contents.find(description_link)
            p_tag = '<p>'
            i1 = contents[i0:].find(p_tag)
            start_index = i0 + i1 + len(p_tag)
            profile = contents[start_index:start_index+300]
            return HttpResponse(profile)
        except Exception as e:
            err_msg = 'Err:' + e.message
            raise Http404(err_msg)
    else:
        raise Http404('Invalid request.')




