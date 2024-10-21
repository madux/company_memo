odoo.define('portal_request.attendance_form_template', function (require) {
    "use strict";

    require('web.dom_ready');
    var utils = require('web.utils');
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;  
    
     

    publicWidget.registry.PortalRequestAttendanceWidgets = publicWidget.Widget.extend({
        selector: '#attendance-request-form',
        start: function(){
            var self = this;
            return this._super.apply(this, arguments).then(function(){
                console.log("Attendance has started")
            });
        },
        willStart: function(){
            var self = this; 
            return this._super.apply(this, arguments).then(function(){
                console.log("Attendance.....")
            })
        },
        events: {
            'click .btn-checkinout': function(ev){
                let targetElement = $(ev.target).attr('id');
                console.log(`Attendance checkout out ${targetElement}`)
                this._rpc({
                    route: `/attendance/check`,
                    params: {
                        'type': targetElement == 'checked_in' ? 'in' : 'out',
                    },
                }).then(function (data) {
                    if(data.status){
                        console.log('updating attendance record data => '+ JSON.stringify(data))
                        window.location.href = `/portal/attendance`;
                        // if (targetElement == 'checked_in'){
                        //     // $('#checked_in').addClass('d-none');
                        //     window.location.href = `/portal/attendance`;
                        // }else {
                        //     window.location.href = `/portal/attendance`;
                        // }
                    }else{
                        // alert(data.message);

                    }
                    
                }).guardedCatch(function (error) {
                    let msg = error.message.message
                    alert(`Unknown Error! ${msg}`)
                });
            },
         },
         

    });

// return PortalRequestWidget;
});