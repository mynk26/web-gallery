from django.urls import path
from .views import AddPhotoView,KeyImagesView,Img, ImgDelete,DeleteSuggestionsView,DeleteImageView, CopyImage, MoveImage, AddFolder, RenameView, SearchByFace, DeleteFolder, LikeImage,LikedImagesView, MultiOps,downloadfiles,downloadsaved, lastseenupdate


urlpatterns = [
    path('addphoto/',AddPhotoView.as_view()),
    path('link/deletesuggestions/',DeleteSuggestionsView.as_view()),
    path('link/liked/',LikedImagesView.as_view()),
    path('links/<str:key>/',KeyImagesView.as_view()),
    path('copy/<str:key>/<path:image>',CopyImage.as_view()),
    path('move/<str:thiskey>/<str:key>/<path:image>',MoveImage.as_view()),
    path('media/ImageData/<str:user_username>/<str:type>/<str:img_name>',Img.as_view()),
    path('deleteview/media/ImageData/<str:user_username>/<str:type>/<str:img_name>', ImgDelete.as_view()),
    path('delete/<path:image>',DeleteImageView.as_view()),
    path('addfolder/<str:type>',AddFolder.as_view()),
    path('rename/<str:oldname>/<str:newname>', RenameView.as_view()),
    path('link/searchbyface/',SearchByFace.as_view()),
    path('deletefolder/<str:key>',DeleteFolder.as_view()),
    path('like/<int:state>/<path:image>',LikeImage.as_view()),
    path('multiops/',MultiOps),
    path('downloadfiles/',downloadfiles),
    path('downloadsaved/',downloadsaved),
    path('lastseen/<path:img>',lastseenupdate.as_view())
]


