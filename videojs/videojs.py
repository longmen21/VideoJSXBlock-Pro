""" videojsXBlock main Python class"""

import pkg_resources
from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Boolean
from xblock.fragment import Fragment
import time


class videojsXBlock(XBlock):
    '''
    Icon of the XBlock. Values : [other (default), video, problem]
    '''
    icon_class = "video"

    '''
    Fields
    '''
    display_name = String(display_name="Display Name",
                          default="Video JS",
                          scope=Scope.settings,
                          help="This name appears in the horizontal navigation at the top of the page.")

    url = String(display_name="Video URL",
                 default="http://vjs.zencdn.net/v/oceans.mp4",
                 scope=Scope.content,
                 help="The URL for your video.")

    allow_download = Boolean(display_name="Video Download Allowed",
                             default=True,
                             scope=Scope.content,
                             help="Allow students to download this video.")

    source_text = String(display_name="Source document button text",
                         default="",
                         scope=Scope.content,
                         help="Add a download link for the source file of your video. Use it for example to provide the PowerPoint or PDF file used for this video.")

    source_url = String(display_name="Source document URL",
                        default="",
                        scope=Scope.content,
                        help="Add a download link for the source file of your video. Use it for example to provide the PowerPoint or PDF file used for this video.")

    start_time = String(display_name="Start time",
                        default="",
                        scope=Scope.content,
                        help="The start and end time of your video. Equivalent to 'video.mp4#t=startTime,endTime' in the url.")

    end_time = String(display_name="End time",
                      default="",
                      scope=Scope.content,
                      help="The start and end time of your video. Equivalent to 'video.mp4#t=startTime,endTime' in the url.")

    sub_title_url = String(display_name="sub_title",
                           default="",
                           scope=Scope.content,
                           help="The link of subtitle.")

    '''
    Util functions
    '''

    def load_resource(self, resource_path):
        """
        Gets the content of a resource
        """
        resource_content = pkg_resources.resource_string(__name__, resource_path)
        return resource_content.decode('utf-8')

    def render_template(self, template_path, context={}):
        """
        Evaluate a template by resource path, applying the provided context
        """
        template_str = self.load_resource(template_path)
        return Template(template_str).render(Context(context))

    '''
    Main functions
    '''

    def student_view(self, context=None):
        """
        The primary view of the XBlock, shown to students
        when viewing courses.
        """
        fullUrl = self.url
        if self.start_time != "" and self.end_time != "":
            fullUrl += "#t=" + self.start_time + "," + self.end_time
        elif self.start_time != "":
            fullUrl += "#t=" + self.start_time
        elif self.end_time != "":
            fullUrl += "#t=0," + self.end_time

        context = {
            'display_name': self.display_name,
            'url': fullUrl,
            'allow_download': self.allow_download,
            'source_text': self.source_text,
            'source_url': self.source_url,
            'subtitle_url': self.sub_title_url,
            'id': time.time()
        }
        html = self.render_template('public/html/videojs_view.html', context)

        frag = Fragment(html)
        frag.add_css(self.load_resource("public/css/video-js.css"))
        frag.add_javascript(self.load_resource("public/js/video-js.min.js"))

        frag.add_css(self.load_resource("public/css/videojs.css"))
        # frag.add_css_url(self.runtime.local_resource_url(self, 'public/css/video-js.css'))
        # frag.add_javascript_url(self.runtime.local_resource_url(self, 'public/js/video-js.min.js'))

        frag.add_javascript(self.load_resource("public/js/videojs_view.js"))
        frag.initialize_js('videojsXBlockInitView')
        return frag

    def studio_view(self, context=None):
        """
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        """
        context = {
            'display_name': self.display_name,
            'url': self.url,
            'allow_download': self.allow_download,
            'source_text': self.source_text,
            'source_url': self.source_url,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'sub_title': self.sub_title_url
        }
        html = self.render_template('public/html/videojs_edit.html', context)

        frag = Fragment(html)
        frag.add_javascript(self.load_resource("public/js/videojs_edit.js"))
        # frag.add_javascript(self.load_resource("public/js/video-js.min.js"))
        # frag.add_css(self.load_resource("public/css/video-js.css"))
        #frag.add_resource_url(self.runtime.local_resource_url(self, 'public/font/vjs.eot'))
        #frag.add_resource_url(self.runtime.local_resource_url(self, 'public/font/vjs.svg'), 'image/svg+xml')
        #frag.add_resource_url(self.runtime.local_resource_url(self, 'public/font/vjs.ttf'))
        #frag.add_resource_url(self.runtime.local_resource_url(self, 'public/font/vjs.woff'), 'application/x-font-woff')

        frag.add_resource_url(self.runtime.local_resource_url(self, 'public/img/loading.gif'), 'image/gif')
        frag.initialize_js('videojsXBlockInitStudio')
        return frag

    @XBlock.json_handler
    def save_videojs(self, data, suffix=''):
        """
        The saving handler.
        """
        self.display_name = data['display_name']
        self.url = data['url']
        self.allow_download = True if data['allow_download'] == "True" else False  # Str to Bool translation
        self.source_text = data['source_text']
        self.source_url = data['source_url']
        self.start_time = ''.join(data['start_time'].split())  # Remove whitespace
        self.end_time = ''.join(data['end_time'].split())  # Remove whitespace
        self.sub_title_url = data['sub_title']

        return {
            'result': 'success',
        }

    @XBlock.json_handler
    def tracking_log(self, data, suffix=''):
        msg = data['msg']
        type = data['type']
        self.runtime.publish(self, type, msg)
        return {
            'result': 'success'
        }
