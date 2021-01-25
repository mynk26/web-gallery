from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from .models import Links
from .forms import AddImageForm,AddFolderForm, SearchImageForm ,AddFaceFolderForm
from django.views.generic.edit import FormView
from django.http import HttpResponse, FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
import face_recognition, cv2
from PIL import Image
from .models import Images
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from datetime import date, timedelta
import os,json
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

import tempfile,zipfile
from wsgiref.util import FileWrapper


# Create your views here.
class AddPhotoView(FormView):
    def get(self, request):
        user = request.user
        if str(user) =='AnonymousUser':
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        form = AddImageForm()
        return render(request,'AddImage.html',{'form':form})
    def post(self,request):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        image_list = request.FILES.getlist('images')
        if len(image_list)==0:
            return HttpResponse("<script>window.location.href = './';alert('Upload atleast one file...!!!');</script>")
        status = None
        for image in image_list:
            img_obj = Images.objects.create(user = user)
            img_obj.image = image
            print(type(image))
            im = Image.open(img_obj.image)
            thumb = im.convert('RGB')
            thumb.thumbnail((200,200))
            thumb_io = BytesIO()
            thumb.save(thumb_io,im.format)
            thumb_file = InMemoryUploadedFile(
                file=thumb_io,
                field_name=None,
                name=img_obj.image.name,
                content_type=image.content_type,
                size=image.size,
                charset=None
            )
            img_obj.thumb = thumb_file
            img_obj.save()
            im.close()
            img_path = str(img_obj.image)[:]
            thumb_path = str(img_obj.thumb)[:]
            del img_obj
            path=(img_path,thumb_path,str(timezone.now().date()))
            status = self.Linking(user,path)
            if status != 'OK':
                break
        if status == 'OK':
            return HttpResponse("<script> alert('"+str(len(image_list))+" Files uploaded'); window.location.href='../links/All'</script>")
        return HttpResponse(status)


    def Linking(self,user,path):
        try:
            print(path[0])
            img = face_recognition.load_image_file(path[0])
            print('here')
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            facedata_list = face_recognition.face_encodings(img)
            if len(facedata_list) == 0:        # no face found
                print('No face Found')
                return 'OK'
            else:
                try:
                    link_obj = Links.objects.get(user=user)
                except Exception as e:
                    print(e.__str__()+'01')
                    return HttpResponse(e.__str__())
                link = link_obj.link
                face_link_list = link['face_keys'][:]
                if len(face_link_list)==0:
                    link['face_keys'] = []
                    count = 0
                    for facedata in facedata_list:
                        while ('Face'+str(count+1)) in link.keys():
                            count+=1
                        link['Face' + str(count + 1)]={}
                        link['Face'+str(count+1)]['Image_list'] = [path,]
                        link['Face'+str(count+1)]['faceEnc'] = [facedata,]
                        link['face_keys'].append('Face'+str(count+1))
                        count+=1
                else:
                    for facedata in facedata_list:
                        count = 0
                        print('1')
                        for key in face_link_list:
                            print('2')
                            if face_recognition.compare_faces(link[key]['faceEnc'],facedata)[0]:
                                print('3')
                                link[key]["Image_list"].append(path)
                                count=1
                                break
                        if count == 0:
                            keygen = len(face_link_list)
                            while ('Face'+str(keygen+1)) in link.keys():
                                keygen+=1
                            link['Face' + str(keygen + 1)] = {}
                            link['Face' + str(keygen+1)]["Image_list"] = [path, ]
                            link['Face' + str(keygen+1)]["faceEnc"] = [facedata, ]
                            link['face_keys'].append('Face' + str(keygen+1))
                            face_link_list.append('Face' + str(keygen+1))
                link_obj.link = link
                link_obj.save()
                print(link)
                del img
                return 'OK'
        except Exception as e:
            print(e.__str__()+'02')
            return(e.__str__())

def LoadList(imgs,type):
    ttoi={}                                                 # thumb address to index and
    itot={}                                                 # index to thumb address
    ttod = {}                                                  #thumb to date
    count=0
    if type=='All':
        temp_date = imgs[0].date
        ttod[str(imgs[0].thumb)]=str(temp_date.strftime("%d-%m-%Y"))
        for img in imgs:
            ttoi[str(img.thumb)]=count
            itot[count]={'thumb': str(img.thumb),'image': str(img.image)}
            if temp_date != img.date:
                temp_date = img.date.strftime("%d-%m-%Y")
                ttod[str(img.thumb)] = str(temp_date)
            count+=1
    else:
        try:
            temp_date = imgs[0][2]
            ttod[str(imgs[0][1])] = str(temp_date.strftime("%d-%m-%Y"))
            for img in imgs:
                ttoi[str(img[1])]=count
                itot[count]={'thumb': str(img[1]),'image': str(img[0])}
                if temp_date != img[2]:
                    temp_date = img[2]
                    ttod[str(img[1])] = str(temp_date.strftime("%d-%m-%Y"))
                count+=1
            print(ttod)
        except  Exception as e:
            print(e.__str__())
            return e.__str__()

    return {'itot':json.dumps(itot),'ttoi':json.dumps(ttoi),'ttod':json.dumps(ttod)}


class KeyImagesView(View):
    def get(self,request,key):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            if len(Images.objects.filter(user=user))==0:
                return HttpResponse("<script>window.location.href = '../../addphoto';alert('add image first');</script>")
            if key == 'All':
                img = Images.objects.filter(user=user).order_by('-date')
                try:
                    itmap=LoadList(img,'All')               #index thumb map
                except:
                    pass
                page = request.GET.get('page', 1)
                paginator = Paginator(img, 5)
                try:
                    images = paginator.page(page)
                except PageNotAnInteger:
                    images = paginator.page(1)
                except EmptyPage:
                    images = paginator.page(paginator.num_pages)
                link_obj = Links.objects.get(user=user)
                folders = link_obj.link
                del folders['face_keys']
                del link_obj
                del img
                return render(request, 'image_index.html', {'images': images,'folders':folders.keys(),'view':'all','itmap':itmap})
                #return render(request,'image_index.html',{'images_thumb':img})
            else:

                ins_link = Links.objects.get(user=user)
                images=list(ins_link.link[key]['Image_list'])
                print(images)
                try:
                    itmap = LoadList(images, 'key')                                         # index thumb map
                except Exception as e:
                    print(e.__str__())
                folders = ins_link.link
                del folders['face_keys']
                del folders[key]
                del ins_link
                return render(request, 'image_index.html', {'images': images,'folders':folders,'thiskey':key,'view':'key','itmap':itmap})
        except Exception as e:
            print(e.__str__())


class Img(View):
    def get(self,request,user_username,type,img_name):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        if type=='All':
            img = open('media/ImageData/' + str(user) + '/All/' + img_name, 'rb')
            im = Images.objects.get(user=user,image=str('media/ImageData/' + str(user) + '/All/' + img_name))
            print('done')
            im.last_seen=timezone.now()
            im.save()
            del im
        else:
            img = open('media/ImageData/'+str(user)+'/thumb/'+img_name,'rb')

        img_read = img.read()
        img.close()
        del img
        return HttpResponse(img_read, content_type="image/jpeg")

class ImgDelete(View):                                                                          #similar view as Img just not updating last seen
    def get(self,request,user_username,type,img_name):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        if type=='All':
            img = open('media/ImageData/' + str(user) + '/All/' + img_name, 'rb')
        else:
            img = open('media/ImageData/'+str(user)+'/thumb/'+img_name,'rb')
        img_read = img.read()
        img.close()
        del img
        return HttpResponse(img_read, content_type="image/jpeg")

class DeleteSuggestionsView(View):
    def get(self,request):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            img = Images.objects.filter(user=user,last_seen__lte= date.today() - timedelta(days=150),like=False)
            if len(img)==0:
                return HttpResponse("<script>window.location.href = '../../links/All/';alert('No image found with lastseen more than 150 days!!!!!');</script>")
            itmap = LoadList(img,'All')
            page = request.GET.get('page', 1)
            paginator = Paginator(img, 2)
            try:
                images = paginator.page(page)
            except PageNotAnInteger:
                images = paginator.page(1)
            except EmptyPage:
                images = paginator.page(paginator.num_pages)
            ins_link = Links.objects.get(user=user)
            folders = ins_link.link
            del folders['face_keys']
            del ins_link
            return render(request, 'image_index.html', {'images': images,'folders':folders,'view':'delete','itmap':itmap})
                # return render(request,'image_index.html',{'images_thumb':img})
        except Exception as e:
            print(e.__str__())

class DeleteImageView(APIView):
    def get(self,request,image):
        user = request.user
        if not  user.is_authenticated:
            return Response("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            img = Images.objects.get(user=user,image=image)
            p=str(img.image)
            t=str(img.thumb)
            d  = str(img.date)
            print(d,'\n\n\n\n\n\n\n\n\n\n')
            result = img.delete()[0]
            if result == 1:
                link_obj = Links.objects.get(user=user)
                link = link_obj.link
                for key in list(link.keys()):
                    if key!='face_keys':
                        if (p,t,d) in link[key]['Image_list']:
                            link[key]['Image_list'].remove((p,t,d))
                link_obj.link = link
                link_obj.save()
                del img
                os.remove(p)
                os.remove(t)
                print(result)
            return Response(data="Deleted")
        except Exception as e:
            print(e.__str__())
            return Response(e.__str__())


class CopyImage(APIView):
    def get(self,request,key,image):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            link_obj = Links.objects.get(user = user)
            img_obj = Images.objects.get(user = user,image=image)
            link = link_obj.link
            print(key)
            if (image,img_obj.thumb) in link[key]['Image_list']:
                link_obj.save()
                del link_obj
                del img_obj
                return Response(data='Already present in '+key)
            link[key]['Image_list'].append((image,img_obj.thumb))
            link_obj.link = link
            link_obj.save()
            del link_obj
            del img_obj
        except Exception as e:
            return Response(data=e.__str__())
        return Response(data='Copied')


class MoveImage(APIView):
    def get(self,request,thiskey,key,image):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            link_obj = Links.objects.get(user = user)
            img_obj = Images.objects.get(user = user,image=image)
            link = link_obj.link
            print(key)
            if key!='Remove':
                if (image,img_obj.thumb) in link[key]['Image_list']:
                    link_obj.save()
                    del link_obj
                    del img_obj
                    return Response(data='Already present in '+key)
                link[key]['Image_list'].append((image,img_obj.thumb))
            link[thiskey]['Image_list'].remove((image,img_obj.thumb))
            link_obj.link = link
            link_obj.save()
            del link_obj
            del img_obj
        except Exception as e:
            return Response(data=e.__str__())
        return Response(data='Moved')

class AddFolder(View):
    def get(self,request,type):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        if type=='face':
            form = AddFaceFolderForm()
        else:
            form = AddFolderForm()
        return render(request,'AddImage.html',{'form':form,'formtype':'Folder'})

    def post(self,request,type):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            form = AddFolderForm(request.POST)
            if form.is_valid():
                name =form.cleaned_data.get('Name')
                link_obj = Links.objects.get(user=user)
                link = link_obj.link
                if name not in list(link.keys()):
                    if type=='face':
                        image = request.FILES.get('Image')
                        img = face_recognition.load_image_file(image)
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        facedata_list = face_recognition.face_encodings(img)
                        if len(facedata_list)!=1:
                            return HttpResponse('<script>top.location.href="../../home/";alert("face folder can only be created with image contains exactly one face");</script>')
                        link_obj = Links.objects.get(user=user)
                        link = link_obj.link
                        for key in link['face_keys']:
                            if face_recognition.compare_faces(link[key]['faceEnc'],facedata_list[0])[0]:
                                return HttpResponse('<script>top.location.href="../../home/";alert("Face already face in '+key+'");</script>')
                        img_obj = Images.objects.create(user=user)
                        img_obj.image = image
                        im = Image.open(img_obj.image)
                        thumb = im.convert('RGB')
                        thumb.thumbnail((200, 200))
                        thumb_io = BytesIO()
                        thumb.save(thumb_io, im.format)
                        thumb_file = InMemoryUploadedFile(
                            file=thumb_io,
                            field_name=None,
                            name=img_obj.image.name,
                            content_type=image.content_type,
                            size=image.size,
                            charset=None
                        )
                        img_obj.thumb = thumb_file
                        img_obj.save()
                        link[name] = {'Image_list': [(img_obj.image,img_obj.thumb),],'faceEnc':facedata_list}
                        link['face_keys'].append(name)
                        print(link)
                    else:
                        link[name] = {'Image_list': [], }
                else:
                    return HttpResponse('<script>alert("folder already exist with this name!!!");</script>')
                link_obj.link = link
                link_obj.save()
                del link_obj
                return HttpResponse('<script>top.location.href="../../home/";alert("folder created.");</script>')
        except Exception as e:
            return HttpResponse(e.__str__())

class DeleteFolder(View):
    def get(self,request,key):
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            link_obj = Links.objects.get(user=user)
            link = link_obj.link
            if key in link.keys():
                del link[key]
                if key in link['face_keys']:
                    link['face_keys'].remove(key)
            link_obj.link=link
            link_obj.save()
            del link_obj
            return HttpResponse('<script>top.location.href="../../home/"; alert("'+key+' Deleted");</script>')
        except Exception as e:
            return HttpResponse(e.__str__())

class RenameView(APIView):
    def get(self,request,oldname,newname):
        user = request.user
        if not  user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            link_obj = Links.objects.get(user=user)
            link = link_obj.link
            link[newname]=link[oldname]
            if oldname in link['face_keys']:
                link['face_keys'].remove(oldname)
                link['face_keys'].append(newname)
            del link[oldname]
            link_obj.link = link
            link_obj.save()
            del link_obj
            return Response(data='Renamed')
        except Exception as e:
            return Response(e.__str__())
        pass

class SearchByFace(View):
    def get(self,request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("<script>window-.location.href = '../';alert('User not Found!!!!!!');</script>")
        form = SearchImageForm()
        return render(request,'AddImage.html',{'form':form})
    def post(self,request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("<script>window-.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            image = request.FILES.get('Image')
            img = face_recognition.load_image_file(image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            facedata_list = face_recognition.face_encodings(img)
            result=[]
            for face in facedata_list:
                link_obj = Links.objects.get(user=user)
                link = link_obj.link
                for key in list(link['face_keys']):
                    if face_recognition.compare_faces(link[key]['faceEnc'],face)[0]:
                        result+=(link[key]['Image_list'])
            itmap = LoadList(result,'link')
            ins_link = Links.objects.get(user=user)
            folders = ins_link.link
            del folders['face_keys']
            del ins_link
            return render(request,'image_index.html',{'images':result,'folders':folders,'view':'search','itmap':itmap})
        except Exception as e:
            return HttpResponse(e.__str__())

class LikeImage(APIView):
    def get(self,request,state,image):
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("<script>window-.location.href = '../';alert('User not Found!!!!!!');</script>")
        img_obj = Images.objects.get(user=user,image=image)
        if state==1:
            if img_obj.like:
                img_obj.like=False
                v=0
            else:
                img_obj.like=True
                v=1
            img_obj.save()
            del img_obj
            return Response(data=json.dumps({'status': v}))
        elif state==0:
            if img_obj.like:
                v=1
            else:
                v=0
            name = str(img_obj.image)[str(img_obj.image).rindex('/')+1:]
            date = str(img_obj.date.strftime("%d-%m-%Y"))
            height = str(img_obj.height)
            width = str(img_obj.width)
            dimensions = height +' x '+width
            size = str("{:.2f}".format(os.path.getsize(str(img_obj.image))/(1024*1024)))+'MB'
            img_obj.save()
            del img_obj
            return Response(data=json.dumps({'status':v,'Name':name,'Date':date,'Dimensions':dimensions,'Size':size}))

class LikedImagesView(View):
    def get(self,request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            img = Images.objects.filter(user=user, like=True)
            itmap = LoadList(img,'All')
            page = request.GET.get('page', 1)
            paginator = Paginator(img, 2)
            try:
                images = paginator.page(page)
            except PageNotAnInteger:
                images = paginator.page(1)
            except EmptyPage:
                images = paginator.page(paginator.num_pages)
            ins_link = Links.objects.get(user=user)
            folders = ins_link.link
            del folders['face_keys']
            del ins_link
            return render(request, 'image_index.html', {'images': images, 'folders': folders,'view':'like','itmap':itmap})
            # return render(request,'image_index.html',{'images_thumb':img})
        except Exception as e:
            print(e.__str__())

def MultiOps(request):
    if request.is_ajax() and request.POST:
        user= request.user
        thumb_lst = request.POST.get('NodeList')[:-1].split(',')
        dest = request.POST.get('destination')
        op = request.POST.get('op')
        total_item =len(thumb_lst)
        if op=='copyop':
            for thumb in thumb_lst:
                try:
                    img_obj = Images.objects.get(user=user, thumb=thumb)
                    CopyImage().get(request=request,key=dest,image=img_obj.image)
                except Exception as e:
                    print(e.__str__())
                    return HttpResponse('failed at ' + thumb, content_type='application/json')
            return HttpResponse(json.dumps({'data':str(total_item)+' copied to '+dest,'status':'1'}), content_type='application/json')
        elif op=='moveop':
            for thumb in thumb_lst:
                try:
                    thiskey = request.POST.get('thiskey')
                    img_obj = Images.objects.get(user=user, thumb=thumb)
                    MoveImage().get(request=request,thiskey=thiskey,key=dest,image=img_obj.image)
                except Exception as e:
                    print(e.__str__())
                    return HttpResponse('failed at ' + thumb, content_type='application/json')
            return HttpResponse(json.dumps({'data':str(total_item)+' moved to '+dest,'status':'1'}), content_type='application/json')
        elif op=='likeop':
            for thumb in thumb_lst:
                try:
                    img_obj = Images.objects.get(user=user, thumb=thumb)
                    LikeImage().get(request=request,state=1,image=img_obj.image)
                except Exception as e:
                    print(e.__str__())
                    return HttpResponse('failed at ' + thumb, content_type='application/json')
            return HttpResponse(json.dumps({'data':str(total_item)+' liked','status':'1'}), content_type='application/json')

        elif op=='deleteop':
            for thumb in thumb_lst:
                try:
                    img_obj = Images.objects.get(user=user, thumb=thumb)
                    DeleteImageView().get(request=request,image=img_obj.image)
                except Exception as e:
                    print(e.__str__())
                    return HttpResponse('failed at '+ thumb, content_type='application/json')
            return HttpResponse(json.dumps({'data':str(total_item)+ ' deleted.','status':'1'}), content_type='application/json')
        elif op=='keepop':
            for thumb in thumb_lst:
                try:
                    img_obj = Images.objects.get(user=user, thumb=thumb)
                    img_obj.last_seen = date.today()
                    img_obj.save()
                    del img_obj
                except Exception as e:
                    print(e.__str__())
                    return HttpResponse('failed at '+ thumb, content_type='application/json')
            return HttpResponse(json.dumps({'data':str(total_item)+ ' items last seen updated','status':'1'}), content_type='application/json')

def downloadfiles(request):
    thumb_lst = request.POST.get('NodeList')[:-1].split(',')
    img_objs = Images.objects.filter(user=request.user, thumb__in=thumb_lst)
    filenames = [str(img_obj.image) for img_obj in img_objs]
    #temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile('media/ImageData/'+str(request.user)+'/selected.zip', 'w', zipfile.ZIP_DEFLATED)
    count=0
    for filename in filenames:
        archive.write(filename, 'file_'+filename[filename.rindex('/')+1:])
        count+=1
    archive.close()

    return HttpResponse(json.dumps({'data':'ok'}))

def downloadsaved(request):
    if not request.user.is_authenticated:
        return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
    f=open('media/ImageData/'+str(request.user)+'/selected.zip','rb')
    return FileResponse(f)


class lastseenupdate(APIView):
    def get(self, request, img):
        if not request.user.is_authenticated:
            return HttpResponse("<script>window.location.href = '../';alert('User not Found!!!!!!');</script>")
        try:
            image = Images.objects.get(user=request.user,image =img)
            image.last_seen=date.today()
            image.save()
            return Response(data='Last Seen Updated')
        except Exception as e:
            return Response(e.__str__())
