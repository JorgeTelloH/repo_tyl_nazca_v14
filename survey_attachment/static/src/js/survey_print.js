odoo.define('survey_attachment.print', function (require) {
'use strict';


var publicWidget = require('web.public.widget');

publicWidget.registry.SurveyPrintWidget.include({

    events: {
        'click #_onClick': '_onDownloadClick',
    },


    _onDownloadClick: function (ev) {
       function dataURLtoFile(dataurl, filename) {

        var arr = dataurl.split(','),
            mime = arr[0].match(/:(.*?);/)[1],
            bstr = atob(arr[1]),
            n = bstr.length,
            u8arr = new Uint8Array(n);

        while(n--){
            u8arr[n] = bstr.charCodeAt(n);
        }

        return new File([u8arr], filename, {type:mime});
        }

       var valor = $("#data64")
       var filename = $("#filename")[0].innerText
       var valor = valor[0].innerText
       var file = dataURLtoFile(valor,filename);

       var element = document.createElement('a');
       element.setAttribute('href', valor);
       element.setAttribute('download', filename);

       element.style.display = 'none';
       document.body.appendChild(element);

       element.click();

       document.body.removeChild(element);

    },


});


});