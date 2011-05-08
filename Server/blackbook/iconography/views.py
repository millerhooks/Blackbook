from models import *
from forms import *
from django.shortcuts import get_object_or_404, get_list_or_404

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from forms import TagForm

def index(request):
    form = TagForm()
    
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.client = plan.client
            obj.save()
            
    return render_to_response('iconography/tagupload.html', {
        'form'     :    form,         
        'request'  :    request,
        },
        context_instance=RequestContext(request))
