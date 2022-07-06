odoo.define('survey_attachment.file', function (require) {
'use strict';

var SurveyForm = require("survey.form");
var publicWidget = require('web.public.widget');

publicWidget.registry.SurveyFormWidget.include({
    _onChangeInputFile: function (event) {
        const handleChange = (evt) => {
        var tgt = evt.target || window.event.srcElement,
            files = tgt.files;
        // FileReader support
        const file = files[0];
        const fileType = file["type"];
        var file_name = file["name"]
        const validImageTypes = ["image/gif", "image/jpeg", "image/png", "application/pdf", "text/csv",
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"];
        if (validImageTypes.includes(fileType))
            if (FileReader && files && files.length) {
                var fr = new FileReader()
                fr.onload = function () {
                    const { result } = fr;
                    window.fr = result; // file es el archivo, result es el contenido
                    window.name = file_name;
                };
                fr.readAsDataURL(files[0]);
            } else {
                // Not supported
                // fallback -- perhaps submit the input to an iframe and temporarily store
                // them on the server until the user's session ends.
            }
    };
    handleChange(event);
    },
    _prepareSubmitValues: function (formData, params) {
        var self = this;
        formData.forEach(function (value, key) {
            switch (key) {
                case 'csrf_token':
                case 'token':
                case 'page_id':
                case 'question_id':
                    params[key] = value;
                    break;
            }
        });

        // Get all question answers by question type
        this.$('[data-question-type]').each(function () {
            switch ($(this).data('questionType')) {
                case 'text_box':
                case 'char_box':
                case 'numerical_box':
                    params[this.name] = this.value;
                    break;
                case 'date':
                    params = self._prepareSubmitDates(params, this.name, this.value, false);
                    break;
                case 'datetime':
                    params = self._prepareSubmitDates(params, this.name, this.value, true);
                    break;
                case 'simple_choice_radio':
                case 'multiple_choice':
                    params = self._prepareSubmitChoices(params, $(this), $(this).data('name'));
                    break;
                case 'matrix':
                    params = self._prepareSubmitAnswersMatrix(params, $(this));
                    break;
                case 'upload_file':
                if (window.fr) {
                    params[this.name] = window.fr.concat(',', window.name);
                    /*console.log(window.fr.concat('/', window.name));*/
                    break;
                }
            }
        });
    },
    events: _.extend(
        {
            'change #files': '_onChangeInputFile',
        },
        publicWidget.registry.SurveyFormWidget.prototype.events
    ),
    
});

});