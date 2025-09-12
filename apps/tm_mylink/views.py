from django.shortcuts import render,redirect,get_object_or_404
from apps.tm_mylink.models import inquiry_db
from .forms import MemoModelForm
from django.contrib.auth.decorators import login_required
# Create your views here.

def inquiry_list_all(request) :
    inquiry_dbs = inquiry_db.objects.all()
    context = {
        'inquiry_dbs':inquiry_dbs
    }
    return render (request,'tm_mylink/inquiry_list.html',context )

@login_required
def inquiry_list(request) :
    inquiry_dbs = inquiry_db.objects.filter(author=request.user)
    context = {
        'inquiry_dbs':inquiry_dbs
    }
    return render(request, 'tm_mylink/inquiry_list.html', context)


@login_required
def inquiry_write(request) :
    if request.method=='POST' :
        form = MemoModelForm(request.POST)
        if form.is_valid() :
            inquiry_db=form.save(commit=False)
            inquiry_db.author = request.user
            inquiry_db.save()            
            return redirect('tm_mylink:inquiry_list')
            
    else :
        form = MemoModelForm()
        context ={
            'form':form
        }
        return render(request, 'tm_mylink/inquiry.html', context)
    


def inquiry_detail(request, pk) :
    inquiry_dbs = get_object_or_404(inquiry_db, pk=pk)
    context ={
        'inquiry_dbs':inquiry_dbs
    }
    return render(request, 'tm_mylink/inquiry_detail.html', context)

def inquiry_edit(request, pk) :    
    inquiry_dbs = get_object_or_404(inquiry_db, pk=pk)
    
    if request.method =='POST' :        
        form = MemoModelForm(request.POST, instance=inquiry_dbs)                
        if form.is_valid() :
            form.save()
            return redirect('tm_mylink:inquiry_detail',pk=pk)
    else :
        form = MemoModelForm(instance=inquiry_dbs)
        context ={
            'form':form
        }
        return render(request, 'tm_mylink/inquiry_edit.html', context)

def inquiry_delete(request, pk) :
    inquiry_dbs = get_object_or_404(inquiry_db, pk=pk)
    if request.method=='POST' :
        inquiry_dbs.delete()
        return redirect('tm_mylink:inquiry_list')
    else : 
        return redirect('tm_mylink:inquiry_detail',pk=pk)