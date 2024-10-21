odoo.define('portal_request.portal_dashboard_form_template', function (require) {
    "use strict";

    require('web.dom_ready');
    var utils = require('web.utils');
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;  
    
     

    publicWidget.registry.PortalDashboardFormWidgets = publicWidget.Widget.extend({
        selector: '#portal-dashboard-content',
        start: function(){
            var self = this;
            return this._super.apply(this, arguments).then(function(){
                console.log("portalDashboard has started")
                var doughnut = document.getElementById("doughnutCanvas").getContext("2d");
                new Chart(doughnut, {
                    type: 'doughnut',
                    data: {
                        labels: ['a', 'b', 'c', 'd'],
                        datasets: [{
                        label: '# of',
                        data: [50, 30, 15, 5],
                        borderWidth: 1, 
                        backgroundColor: [
                            'rgba(99, 24, 36, 0.733)',
                        'rgba(107, 27, 197, 0.89)',
                        'rgba(24, 228, 201, 0.89)',
                        'rgba(175, 207, 87, 0.89)',
                        'rgba(218, 8, 36, 0.89)',
                        'rgba(129, 39, 117, 0.89)',
                        'rgba(10, 41, 82, 0.89)',
                        'rgba(35, 103, 190, 0.89)',
                        'rgba(4, 187, 80, 0.89)',
                        'rgba(rgba(158, 47, 64, 0.733)',
                        ]
                        }]
                    },
                    options: {
                        scales: {
                        y: {
                            beginAtZero: true
                        }
                        },
                        aspectRatio: 1.5,
                    }
                });
            });
        },
        willStart: function(){
            var self = this; 
            return this._super.apply(this, arguments).then(function(){
                console.log("portalDashboard.....")
                $('#footer').addClass('d-none');
                $('#o_main_nav').addClass('d-none');
            })
        },
        events: {
            'click .opennavbtn': function(ev){
                console.log(`Opening of navbar`)
                document.getElementById("mysidebar").style.width = "250px";
                $('.closenavbtn').removeClass('d-none');
                $('.opennavbtn').addClass('d-none'); 
            },
            'click .closenavbtn': function(ev){
                console.log(`Closing of navbar`)
                document.getElementById("mysidebar").style.width = "0px";
                $('.opennavbtn').removeClass('d-none');
                $('.closenavbtn').addClass('d-none');
            },

            'click .closeSb': function(ev){
                console.log(`Closing of navbar`)
                document.getElementById("mysidebar").style.width = "0px";
                $('.opennavbtn').removeClass('d-none');
                $('.closenavbtn').addClass('d-none');
            },
         },
         

    });
});