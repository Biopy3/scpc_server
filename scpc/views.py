from django.shortcuts import render

# Create your views here.
from .models import Record
from django.http import FileResponse, HttpResponse
from django import forms
import os, sys, string, random, uuid, subprocess, shutil,time

class UserInfo(forms.Form):
    modelist = [
      ["K80","K80"],["JC69","JC69"],["F81","F81"],["K81","K81"],
      ["F84","F84"],["T92","T92"],["TN93","TN93"],["GG95","GG95"],
      ["LOGDET","LOGDET"],["BH87","BH87"],["PARALIN","PARALIN"],["N","N"],
      ["TS","TS"],["TV","TV"],["INDEL","INDEL"],["INDELBLOCK","INDELBLOCK"]
    ]

    fastafile = forms.FileField(widget=forms.FileInput(attrs={'style':'color:red'}),
                                error_messages={'required':u'please full in correct fast file'})
    newickfile = forms.FileField(widget=forms.FileInput(attrs={'style':'color:red'}),
                                error_messages={'required':u'please full in correct newcik file'})
    model = forms.ChoiceField(label='model',choices=modelist)

modelist = [ "K80","RAW", "JC69", "F81", "K81", "F84", "T92", "TN93","GG95", "LOGDET", "BH87", "PARALIN", "N", "TS", "TV","INDEL", "INDELBLOCK"]

userinfo = UserInfo()

def juge_os_and_set_PATH():
    if os.name == 'posix' and sys.version_info[0] == 3:
        os.environ['PATH'] = os.environ['PATH'] + ':' + os.getcwd() + '/scpc/softwares'
    else:
        os.environ['PATH'] = os.environ['PATH'] + ';' + os.getcwd() + '/scpc/softwares'

#when server is run, blow function will run for adding softwares path
juge_os_and_set_PATH()

def homepage( request):
    return render(request, "homepage.html", {'userinfo': userinfo, 'modelist': modelist})

def save_post(request):
    if request.method == "POST":
        user_input = UserInfo(request.POST,request.FILES) #request.POST is include all data
        if user_input.is_valid():
            fastafile = request.FILES['fastafile']
            newickfile = request.FILES['newickfile']
            model = user_input.cleaned_data['model']
            access_code = str(uuid.uuid1())
            
            record = Record.objects.create(fastafile=fastafile,newickfile=newickfile,access_code=access_code)
            fastafile_path = record.fastafile.path
            newickfile_path = record.newickfile.path

            dir_path = os.path.split(fastafile_path)[0] + '/' +time.strftime('%Y%m%d-%H-%M')
            os.mkdir(dir_path)

            subprocess.call(['scpc','-s', fastafile_path, '-t', newickfile_path, '-m', model, '-o', dir_path])
            shutil.move(fastafile_path, dir_path)
            shutil.move(newickfile_path, dir_path)
            shutil.make_archive(dir_path,'zip',dir_path)
            shutil.rmtree(dir_path)
            
            record = Record.objects.get(access_code=access_code)
            record.resultfile = dir_path + '.zip'
            record.save()
            return HttpResponse('click the url to download your results: <a href=http://45.76.122.117:8000/scpc/download_results/'+access_code+'>\
                                http://45.76.122.117:8000/scpc/download_results/' + access_code + '</a>',)
        else :
          return HttpResponse("errors")
    else:
        return HttpResponse("errors")

def download_results(request,access_code):
    try:
        record_ = Record.objects.get(access_code=access_code)
        fname = record_.resultfile.path
        the_file_name = fname.split('/')[-1]  # 显示在弹出对话框中的默认的下载文件名
        response = FileResponse(open(fname,'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(the_file_name)
        return response
    except:
        return HttpResponse("Can't find file!")