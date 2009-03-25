from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words

class ManyToManySearchInput(forms.SelectMultiple):
    class Media:
        css = {
            'all': ('jautocomplete/jquery.autocomplete.css',)
        }
        js = (
            'jquery.min.js',
            'jautocomplete/lib/jquery.bgiframe.min.js',
            'jautocomplete/lib/jquery.ajaxQueue.js',
            'jautocomplete/jquery.autocomplete.js'
        )

    def label_for_value(self, value):
        return ''

    def __init__(self, rel, search_fields, attrs=None, autocomplete_url='/search/'):
        self.autocomplete_url = autocomplete_url
        self.rel = rel
        self.search_fields = search_fields
        super(ManyToManySearchInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        #print name, value[0], self.rel
        #rendered = super(ManyToManySearchInput, self).render(name,value,  attrs)
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        ul=""
        select=''
        ToModel=self.rel.to
        if not value:value=[]
        for val in value:
            obj=ToModel.objects.get(pk=val)
            ul+="<li id='%(pk)s'><div class='object_repr'>%(repr)s</div><div class='delete_from_m2m'><a style='cursor:pointer'><img src='%(admin_media_prefix)simg/admin/icon_deletelink.gif' /></a></div></li>"%{'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
                        'repr':obj.__unicode__(), 
                        'pk':str(obj.pk)}
            select+='<option id="%(pk)s" value="%(pk)s" selected="selected">%(repr)s</option>'%{'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
                        'repr':obj.__unicode__(), 
                        'pk':str(obj.pk)}
        return mark_safe(u'''
            <style type="text/css" media="screen">
                #lookup_%(name)s {
                    padding-right:16px;
                    width:150px;
                    background: url(
                        %(admin_media_prefix)simg/admin/selector-search.gif
                    ) no-repeat right;
                }
                #del_%(name)s {
                    display: none;
                }
                #list_%(name)s{
                margin-left:5px;
                list-style-type:none
                padding:0;
                margin:0;
                margin-left:75px;
                
                }
                #list_%(name)s li{
                list-style-type:none;
                
                margin:0px;
                padding:0px;
                margin-top:5px;
                }
                .object_repr{
                                float:left;
                                padding-left:2px;
                                border:1px solid #CCCCCC;
                                width:200px;
                                color:#333333;
                                background-color:#EFEFEF;
                                }
                .delete_from_m2m{float:left}
                        
                
            </style>
<select multiple="multiple" name="%(name)s" id="id_%(name)s">
%(select)s
</select>

<input type="text" id="lookup_%(name)s" value="%(label)s" />
<a href="../../../%(app_label)s/%(model_name)s/add/" class="add-another" id="add_id_%(name)s" onclick="return showAddAnotherPopup(this);"> <img src="%(admin_media_prefix)simg/admin/icon_addlink.gif" width="10" height="10" alt="Yenisini Ekle"/></a>
<br/>
<br/>

<ul id="list_%(name)s"><b>Objets s&eacute;l&eacute;ctionn&eacute;s:</b>
%(ul)s
</ul>
<br/>
<br/>

<script type="text/javascript">
            $(document).ready(function() {
            $('#id_%(name)s').hide();
            $('#id_%(name)s').parent().children().filter('.add-another:last').hide();

            //$('#add_id_%(name)s').hide();
            $('.delete_from_m2m').click(function(){
            var rm_li=$(this).parent();
            var rm_pk=$(rm_li).attr("id");
            $('ul#list_%(name)s li#'+rm_pk+':first').remove()
            $('#id_%(name)s #'+rm_pk+':first').remove()
            });
        });
            $('#lookup_%(name)s').keydown( function(){$('#busy_%(name)s').show();});
            
            $('#lookup_%(name)s')
            var event=$('#lookup_%(name)s').autocomplete('%(autocomplete_url)s', {
                extraParams: {
                    search_fields: '%(search_fields)s',
                    app_label: '%(app_label)s',
                    model_name: '%(model_name)s',
                },
                mustMatch: true,
                matchContains: false,
                minChars: 0,
        		width: 320,
        		max: 25,
        		highlight: false,
        		scroll: true,
        		scrollHeight: 500,
        		formatItem: function(data, i, n, value) {
        			return value.split(".")[0];
        		},
        		formatResult: function(data, value) {
        			return value.split(".")[0];
        		}
            });
            event.result(function(event, data, formatted) {
                $('#busy_%(name)s').hide();
                if (data) {
                    var elem=$('#list_%(name)s li#'+data[1])
                    
                    if (!elem.attr("id")){
                    $('#list_%(name)s').html($('#list_%(name)s').html()+'<li id="'+data[1]+'"><div class="object_repr">'+data[0]+'</div><div class="delete_from_m2m"><a style="cursor:pointer"><img src="%(admin_media_prefix)simg/admin/icon_deletelink.gif" /></a></div></li>');
                    $('#lookup_%(name)s').val('');
                    $('#id_%(name)s').html($('#id_%(name)s').html()+'<option id="'+data[1]+'" value="' +data[1] + '" selected="selected">' +data[0] +'</option>');
            $('.delete_from_m2m').click(function(){
            var rm_li=$(this).parent();
            var rm_pk=$(rm_li).attr("id");
            $('ul#list_%(name)s li#'+rm_pk+':first').remove()
            $('#id_%(name)s #'+rm_pk+':first').remove()
            });
                    }
                }
            });
            
            </script>
        ''') % {
            'search_fields': ','.join(self.search_fields),
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'model_name': self.rel.to._meta.module_name,
            'app_label': self.rel.to._meta.app_label,
            'label': label,
            'name': name,
            'ul':ul, 
            'select':select, 
            'autocomplete_url': self.autocomplete_url,
        }

class ForeignKeySearchInput(forms.HiddenInput):
    class Media:
        css = {
            'all': ('jautocomplete/jquery.autocomplete.css',)
        }
        js = (
            'jquery.min.js',
            'jautocomplete/lib/jquery.bgiframe.min.js',
            'jautocomplete/lib/jquery.ajaxQueue.js',
            'jautocomplete/jquery.autocomplete.js'
        )
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        return truncate_words(obj, 14)

    def __init__(self, rel, search_fields, attrs=None, autocomplete_url='/autocomplete'):
        self.autocomplete_url = autocomplete_url
        self.rel = rel
        self.search_fields = search_fields
        super(ForeignKeySearchInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        rendered = super(ForeignKeySearchInput, self).render(name, value, attrs)
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        return rendered + mark_safe(u'''
            <style type="text/css" media="screen">
                #lookup_%(name)s {
                    padding-right:16px;
                    background: url(
                        %(admin_media_prefix)simg/admin/selector-search.gif
                    ) no-repeat right;
                }
                #del_%(name)s {
                    display: none;
                }
            </style>
<input type="text" id="lookup_%(name)s" value="%(label)s" />
<a href="#" id="del_%(name)s">
<img src="%(admin_media_prefix)simg/admin/icon_deletelink.gif" />
</a>
<script type="text/javascript">
            if ($('#lookup_%(name)s').val()) {
                $('#del_%(name)s').show()
            }
            $('#lookup_%(name)s').autocomplete('%(autocomplete_url)s', {
                extraParams: {
                    search_fields: '%(search_fields)s',
                    app_label: '%(app_label)s',
                    model_name: '%(model_name)s',
                },
            }).result(function(event, data, formatted) {
                if (data) {
                    $('#id_%(name)s').val(data[1]);
                    $('#del_%(name)s').show();
                }
            });
            $('#del_%(name)s').click(function(ele, event) {
                $('#id_%(name)s').val('');
                $('#del_%(name)s').hide();
                $('#lookup_%(name)s').val('');
            });
            </script>
        ''') % {
            'search_fields': ','.join(self.search_fields),
            'admin_media_prefix': settings.ADMIN_MEDIA_PREFIX,
            'model_name': self.rel.to._meta.module_name,
            'app_label': self.rel.to._meta.app_label,
            'label': label,
            'name': name,
            'autocomplete_url': self.autocomplete_url,
        }
