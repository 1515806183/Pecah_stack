from django.shortcuts import render
from stack import settings
from django.http import FileResponse
from django.utils.encoding import smart_str
# Create your views here.


def file_download(request):
    file_path = request.GET.get('file_path')
    if file_path:
        # 拼接服务器文件地址
        file_center_dir = settings.SALT_CONFIG_FILES_DIR
        file_path = "%s%s" % (file_center_dir, file_path)
        filename = file_path.split('/')[-1]

        #
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response['X-Sendfile'] = smart_str(file_path)

        return response

    else:
        return KeyError