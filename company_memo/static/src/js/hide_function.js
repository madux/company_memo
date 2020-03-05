odoo.define('memo.hide_edit_buttons', function (require) {
    "use strict";
    let FormView = require('web.FormView');
    var session = require('web.session');
    var Model = require('web.Model');
    var mymodel = new Model('memo.model');
    FormView.include({
        load_record: function (record) {
            if (record && this.$buttons) { 
                if ((this.model === "memo.model") && (record.state != "submit")){
                    if (session.uid !== record.demo_staff){
                        console.log('User '+String(record.demo_staff)+'UID '+session.uid)
                        this.$buttons.find('.o_form_buttons_view').hide();
                            console.log('Hidden at user memo')
                    }
                    else {
                                this.$buttons.find('.o_form_buttons_view').show();
                                console.log('Shown for company memo')
                    } 
                } 
            }
            return this._super(record);
        }
    });
});
