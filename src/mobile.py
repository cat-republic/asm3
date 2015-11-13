#!/usr/bin/python

import additional
import animal
import animalcontrol
import configuration
import diary
import financial
import html
import log
import lookups
import media
import medical
import person
import reports
import smcom
import stock
import users
import utils
from i18n import _, python2display, now, add_days, add_months, add_years, format_currency, format_time
from sitedefs import MULTIPLE_DATABASES
from sitedefs import ELECTRONIC_SIGNATURES, JQUERY_JS, JQUERY_MOBILE_CSS, JQUERY_MOBILE_JS, JQUERY_UI_JS, SIGNATURE_JS, MOMENT_JS, TOUCHPUNCH_JS

def header(l):
    return """<!DOCTYPE html>
    <html>
    <head>
    <title>
    %(title)s
    </title>
    <meta name="viewport" content="width=device-width, initial-scale=1"> 
    %(css)s
    %(scripts)s
    <script type="text/javascript">
        $(document).ready(function() {

            // Flag if we have an idevice
            is_idevice = navigator.userAgent.toLowerCase().indexOf("ipod") != -1 || 
                navigator.userAgent.toLowerCase().indexOf("ipad") != -1 ||
                navigator.userAgent.toLowerCase().indexOf("iphone") != -1;

            // Flag if we have old Android (1/2)
            is_oldandroid = navigator.userAgent.indexOf("Android 2") != -1 ||
                navigator.userAgent.indexOf("Android 1") != -1;

            // If we're on the login page and all the boxes were filled in, 
            // submit it
            if ($("#loginform").size() > 0 && $("#username").val() && $("#password").val()) {
                $("#loginform").submit();
            }

            // If the user sets a new diary date in the future, post it
            $(".diaryon").change(function() {
                $.mobile.changePage("mobile_post?posttype=dia&on=" + $(this).val() + "&id=" + $(this).attr("data"));
            });

            // If the user sets a new incident completed type, post it
            $(".completedtype").change(function() {
                var url = "mobile_post?posttype=vinccomp&ct=" + $(this).val() + "&id=" + $(this).attr("data");
                //$.mobile.changePage(url);
                window.location = url;
            });

            // If the user chooses a test result, post it
            $(".testresult").change(function() {
                $.mobile.changePage("mobile_post?posttype=test&resultid=" + $(this).val() + 
                    "&animalid=" + $(this).attr("data-animal") + "&id=" + $(this).attr("data"));
            });

            $("#home a").attr("data-transition", "slide");

        });
    </script>
    <style>
    .asm-thumbnail {
        max-width: 70px;
        max-height: 70px;
    }
    </style>
    </head>
    <body>
    """ % {
        "title":    _("Animal Shelter Manager", l),
        "css":      html.asm_css_tag("asm-icon.css"),
        "scripts":  html.script_tag(JQUERY_JS) + 
            html.css_tag(JQUERY_MOBILE_CSS) + html.script_tag(JQUERY_MOBILE_JS) 
    }

def jqm_button(href, text, icon = "", ajax = ""):
    if icon != "": icon = "data-icon=\"%s\"" % icon
    if ajax != "": ajax = "data-ajax=\"%s\"" % ajax
    return "<a data-role=\"button\" %(icon)s %(ajax)s href=\"%(href)s\">%(text)s</a>" % { "icon": icon, "ajax": ajax, "href": href, "text": text }

def jqm_checkbox(name, checked = False):
    c = ""
    if checked: c = "checked=\"checked\""
    return "<input type=\"checkbox\" id=\"%s\" name=\"%s\" %s />" % (name, name, c)

def jqm_collapsible(s, icon = ""):
    return "<div data-role=\"collapsible\" data-collapsed=\"true\" data-collapsed-icon=\"%s\">%s</div>\n" % (icon, s)

def jqm_collapsible_set(s):
    return "<div data-role=\"collapsible-set\">%s</div>\n" % s

def jqm_fieldcontain(name, label, inner):
    return "<div data-role=\"fieldcontain\"><label for=\"%(name)s\">%(label)s</label>%(inner)s</div>" % { "name": name, "label": label, "inner": inner }

def jqm_form(name, action="mobile_post", method="post", ajax= ""):
    if ajax != "": ajax = "data-ajax=\"%s\"" % ajax
    return "<form %s id=\"%s\" action=\"%s\" method=\"%s\">\n" % (ajax, name, action, method)

def jqm_form_end():
    return "</form>\n"

def jqm_h3(s):
    return "<h3>%s</h3>\n" % s

def jqm_hidden(name, value):
    return "<input type=\"hidden\" id=\"%(name)s\" name=\"%(name)s\" value=\"%(value)s\" />\n" % { "name": name, "value": value }

def jqm_link(href, text, icon = "", linkclass = "", theme = ""):
    if linkclass != "": linkclass = "class=\"" + linkclass + "\""
    if icon != "": icon = "data-icon=\"" + icon + "\""
    if theme != "": theme = "data-theme=\"" + theme + "\""
    return "<a href=\"%(href)s\" %(linkclass)s %(icon)s %(theme)s>%(text)s</a>\n" % {
        "href": href, "text": text, "icon": icon, "linkclass": linkclass, "theme": theme }

def jqm_list(s, showfilter = False):
    return "<ul data-role=\"listview\" data-filter=\"%s\">\n%s</ul>\n" % (showfilter and "true" or "false", s)

def jqm_list_divider(s):
    return "<li data-role=\"list-divider\" role=\"heading\">%s</li>" % s

def jqm_listitem(s):
    return "<li>%s</li>" % s

def jqm_listitem_link(href, text = "", icon = "", counter = -1, rel = "", ajax = ""):
    counterdisplay = ""
    if counter >= 0: counterdisplay = "<span class=\"ui-li-count ui-btn-up-c ui-btn-corner-all\">%d</span>" % counter
    if icon != "": icon = html.icon(icon)
    if rel != "": rel = "data-rel=\"%s\"" % rel
    if ajax != "": ajax = "data-ajax=\"%s\"" % ajax
    return "<li><a href=\"%(href)s\" %(ajax)s %(rel)s>%(icon)s %(text)s %(counterdisplay)s</a></li>\n" % {
        "href": href, "ajax": ajax, "text": text, "icon": icon, "counterdisplay": counterdisplay, "rel": rel }

def jqm_option(value, label = "", selected = False):
    if selected: selected = "selected=\"selected\""
    if label == "":
        return "<option %s>%s</option>" % (selected, value)
    return "<option value=\"%s\" %s>%s</option>\n" % (value, selected, label)

def jqm_options_next_month(l):
    d = now()
    days = []
    for dummy in xrange(0, 31):
        days.append(jqm_option(python2display(l,d)))
        d = add_days(d, 1)
    d = add_months(now(), 3)
    days.append(jqm_option(python2display(l,d)))
    d = add_months(now(), 6)
    days.append(jqm_option(python2display(l,d)))
    d = add_years(now(), 1)
    days.append(jqm_option(python2display(l,d)))
    return "\n".join(days)

def jqm_options(rs, valuefield, displayfield):
    res = []
    for r in rs:
        res.append(jqm_option(str(r[valuefield]), str(r[displayfield])))
    return "\n".join(res)

def jqm_p(s):
    return "<p>%s</p>\n" % s

def jqm_page_footer():
    return "</div>\n</div>\n"

def jqm_page_header(pageid, title, link = "", backbutton = True):
    backbuttonattr = ""
    if backbutton: backbuttonattr = "data-add-back-btn=\"true\""
    if pageid != "": pageid = "id=\"%s\"" % pageid
    return "<div data-role=\"page\" %(back)s %(pageid)s>\n" \
        "<div data-role=\"header\">" \
        "<h1>%(title)s</h1>%(link)s" \
        "</div>\n" \
        "<div data-role=\"content\">\n" % { 
            "pageid": pageid, "title": title, "link": link, "back": backbuttonattr }

def jqm_select(name, options, selclass = "", data = ""):
    if selclass != "": selclass = "class=\"" + selclass + "\""
    if data != "": data = "data=\"" + data + "\""
    return "<select id=\"%(name)s\" name=\"%(name)s\" %(data)s %(selclass)s>%(options)s</select>\n" % { \
        "name": name, "options": options, "data": data, "selclass": selclass }

def jqm_slider(name, minv = 0, maxv = 0, val = 0):
    return "<input type=\"range\" id=\"%(name)s\" name=\"%(name)s\" value=\"%(val)s\" min=\"%(minv)s\" max=\"%(maxv)s\" />" % { "name": name, "val": val, "minv": minv, "maxv": maxv }

def jqm_span(s):
    return "<span>%s</span>\n" % s

def jqm_submit(label):
    return "<button data-icon=\"check\" type=\"submit\">%s</button>\n" % label

def jqm_table():
    return "<table>\n"

def jqm_table_end():
    return "</table>\n"

def jqm_tablerow(cell1, cell2 = "", cell3 = "", cell4 = ""):
    s = "<tr>\n<td>" + cell1 + "</td>\n"
    if cell2 != "": s += "<td>%s</td>\n" % cell2
    if cell3 != "": s += "<td>%s</td>\n" % cell3
    if cell4 != "": s += "<td>%s</td>\n" % cell4
    s += "</tr>\n"
    return s

def jqm_text(name, value = ""):
    return "<input id=\"%(name)s\" name=\"%(name)s\" value=\"%(value)s\" type=\"text\" />\n" % { "name": name, "value": value }

def page(dbo, session, username):
    """
    Generates the main mobile web page
    dbo: Database info
    """
    l = dbo.locale
    nsa = animal.get_number_animals_on_shelter_now(dbo)
    osa = nsa > 0
    ar = reports.get_available_reports(dbo, False)
    vacc = medical.get_vaccinations_outstanding(dbo)
    test = medical.get_tests_outstanding(dbo)
    med = medical.get_treatments_outstanding(dbo)
    dia = diary.get_uncompleted_upto_today(dbo, username)
    hck = person.get_reserves_without_homechecks(dbo)
    mess = lookups.get_messages(dbo, session.user, session.roles, session.superuser)
    testresults = lookups.get_test_results(dbo)
    stl = stock.get_stock_locations_totals(dbo)
    inmy = animalcontrol.get_animalcontrol_find_advanced(dbo, { "dispatchedaco": session.user, "filter": "incomplete" })
    inop = animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "incomplete" })
    infp = animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "requirefollowup" })
    homelink = jqm_link("mobile", _("Home", l), "home", "ui-btn-right", "b")
    h = []

    def pb(p):
        return users.check_permission_bool(session, p)

    h.append(header(l))

    logoutlink = ""
    if not session.mobileapp: 
        logoutlink = jqm_link("mobile_logout", _("Logout", l), "delete", "ui-btn-right", "b")

    h.append(jqm_page_header("home", "%s : %s" % (username, _("ASM", l)), logoutlink , False))
    items = []
    if configuration.smdb_locked(dbo):
        items.append(jqm_listitem(_("This database is locked and in read-only mode. You cannot add, change or delete records.", l)))
    items.append(jqm_listitem_link("#messages", _("Messages", l), "message", len(mess)))
    if len(ar) > 0 and pb(users.VIEW_REPORT):
        items.append(jqm_listitem_link("#reports", _("Generate Report", l), "report"))
    if pb(users.CHANGE_MEDIA) and ELECTRONIC_SIGNATURES == "touch":
        items.append(jqm_listitem_link("mobile_sign", _("Signing Pad", l), "signature", -1, "", "false"))
    if pb(users.ADD_ANIMAL) or pb(users.VIEW_ANIMAL) or pb(users.CHANGE_VACCINATION) \
       or pb(users.CHANGE_TEST) or pb(users.CHANGE_MEDICAL) or pb(users.ADD_LOG):
        items.append(jqm_list_divider(_("Animal", l)))
    if pb(users.ADD_ANIMAL):
        items.append(jqm_listitem_link("mobile_post?posttype=aas", _("Add Animal", l), "animal-add"))
    if osa and pb(users.VIEW_ANIMAL):
        items.append(jqm_listitem_link("mobile_post?posttype=vsa", _("View Shelter Animals", l), "animal", nsa))
    if len(vacc) > 0 and pb(users.CHANGE_VACCINATION):
        items.append(jqm_listitem_link("#vacc", _("Vaccinate Animal", l), "vaccination", len(vacc)))
    if len(test) > 0 and pb(users.CHANGE_TEST):
        items.append(jqm_listitem_link("#test", _("Test Animal", l), "test", len(test)))
    if len(med) > 0 and pb(users.CHANGE_MEDICAL):
        items.append(jqm_listitem_link("#med", _("Medicate Animal", l), "medical", len(med)))
    if osa and pb(users.ADD_LOG):
        items.append(jqm_listitem_link("#log", _("Add Log to Animal", l), "log", -1, ""))
    if pb(users.ADD_INCIDENT) or pb(users.CHANGE_INCIDENT) or pb(users.VIEW_LICENCE):
        items.append(jqm_list_divider(_("Animal Control", l)))
    if pb(users.ADD_INCIDENT):
        items.append(jqm_listitem_link("mobile_post?posttype=aincs", _("Add Call", l), "call"))
    if len(inmy) > 0 and pb(users.CHANGE_INCIDENT):
        items.append(jqm_listitem_link("#inmy", _("My Incidents", l), "call", len(inmy)))
    if len(inop) > 0 and pb(users.CHANGE_INCIDENT):
        items.append(jqm_listitem_link("#inop", _("Open Incidents", l), "call", len(inop)))
    if len(infp) > 0 and pb(users.CHANGE_INCIDENT):
        items.append(jqm_listitem_link("#infp", _("Incidents Requiring Followup", l), "call", len(infp)))
    if pb(users.VIEW_LICENCE):
        items.append(jqm_listitem_link("#checklicence", _("Check License", l), "licence", -1, ""))
    if pb(users.ADD_DIARY) or pb(users.EDIT_MY_DIARY_NOTES):
        items.append(jqm_list_divider(_("Diary", l)))
    if pb(users.ADD_DIARY):
        items.append(jqm_listitem_link("#diaryadd", _("New Task", l), "diary"))
    if len(dia) > 0 and pb(users.EDIT_MY_DIARY_NOTES):
        items.append(jqm_listitem_link("#diary", _("Complete Tasks", l), "diary", len(dia)))
    if pb(users.CHANGE_STOCKLEVEL):
        items.append(jqm_list_divider(_("Financial", l)))
    if len(stl) > 0 and pb(users.CHANGE_STOCKLEVEL):
        items.append(jqm_listitem_link("#stl", _("Stock Take", l), "stock", len(stl)))
    if pb(users.CHANGE_PERSON):
        items.append(jqm_list_divider(_("Person", l)))
    if len(hck) > 0 and pb(users.CHANGE_PERSON):
        items.append(jqm_listitem_link("#homecheck", _("Perform Homecheck", l), "person", -1, ""))

    h.append(jqm_list("\n".join(items)))
    h.append(jqm_page_footer())

    h += page_messages(l, homelink, mess)
    h += page_message_add(l, homelink, dbo)
    h += page_reports(l, homelink, ar)
    h += page_vaccinations(l, homelink, vacc)
    h += page_tests(l, homelink, test, testresults)
    h += page_medication(l, homelink, med)
    h += page_log_add(l, homelink, dbo)
    h += page_check_licence(l, homelink)
    h += page_diary_add(l, homelink, dbo)
    h += page_diary(l, homelink, dia)
    h += page_homecheck(l, homelink, dbo)
    h += page_stocklevels(l, homelink, stl)
    h += page_incidents(l, homelink, inmy, "inmy", _("My Incidents", l))
    h += page_incidents(l, homelink, inop, "inop", _("Open Incidents", l))
    h += page_incidents(l, homelink, infp, "infp", _("Incidents Requiring Followup", l))

    h.append("</body></html>")
    return "\n".join(h)

def page_sign(dbo, session, username):
    l = session.locale
    ids = configuration.signpad_ids(dbo, username)
    h = []
    h.append("""<!DOCTYPE html>
    <html>
    <head>
    <title>
    %(title)s
    </title>
    <meta name="viewport" content="width=device-width, initial-scale=1"> 
    %(css)s
    %(scripts)s
    <script type="text/javascript">
        $(document).ready(function() {
            $("#signature").signature({ guideline: true });
            $("#sig-clear").click(function() {
                $("#signature").signature("clear");
            });
            $("#sig-home").click(function() {
                window.location = "mobile";
            });
            $("#sig-refresh").click(function() {
                location.reload();
            });
            $("#sig-logout").click(function() {
                window.location = "mobile_logout";
            });
            $("#sig-sign").click(function() {
                var img = $("#signature canvas").get(0).toDataURL("image/png");
                var formdata = "posttype=sign&ids=%(ids)s&sig=" + encodeURIComponent(img);
                formdata += "&signdate=" + encodeURIComponent(moment().format("YYYY-MM-DD HH:mm:ss"));
                $.ajax({
                    type: "POST",
                    url: "mobile_post",
                    data: formdata,
                    dataType: "text",
                    mimeType: "textPlain",
                    success: function(result) {
                        location.reload();
                    },
                    error: function(jqxhr, textstatus, response) {
                        $("body").append("<p>" + response + "</p>");
                    }
                });
            });
            $("#reviewlink").click(function() { 
                $("#reviewlink").fadeOut();
                $("#review").slideDown(); 
            });
        });
    </script>
    <style>
    button { 
        padding: 10px; 
        font-size: 100%%; 
    }
    #signature { 
        border: 1px solid #aaa; 
        height: 200px; 
        width: 100%%;
        max-width: 500px;
    }
    </style>
    </head>
    <body>
    """ % {
        "title":    _("Signing Pad", l),
        "ids":      ids,
        "css":      html.asm_css_tag("asm-icon.css"),
        "scripts":  html.script_tag(JQUERY_JS) + html.script_tag(JQUERY_UI_JS) + 
            html.script_tag(TOUCHPUNCH_JS) + html.script_tag(SIGNATURE_JS) + html.script_tag(MOMENT_JS)
    })
    if ids.strip() == "":
        h.append('<p>%s</p>' % _("Waiting for documents...", l))
        h.append('<p><button id="sig-refresh">' + _("Reload", l) + '</button></p>')
        #h.append('<p><button id="sig-home">' + _("Home", l) + '</button></p>')
        if not session.mobileapp:
            h.append('</p><button id="sig-logout">' + _("Logout", l) + '</button></p>')
    else:
        d = []
        docnotes = []
        for mid in ids.strip().split(","):
            if mid.strip() != "": 
                docnotes.append(media.get_notes_for_id(dbo, int(mid)))
                mdate, medianame, mimetype, contents = media.get_media_file_data(dbo, int(mid))
                d.append(contents)
                d.append("<hr />")
        h.append("<p><b>%s: %s</b></p>" % (_("Signing", l), ", ".join(docnotes)))
        h.append('<p><a id="reviewlink" href="#">%s</a></p>' % _("View Document", l))
        h.append('<div id="review" style="display: none">')
        h.append("\n".join(d))
        h.append('</div>')
        h.append('<div id="signature"></div>')
        h.append('<p>')
        h.append('<button id="sig-clear" type="button">' + _("Clear", l) + '</button>')
        h.append('<button id="sig-sign" type="button">' + _("Sign", l) + '</button>')
        h.append('</p>')
        h.append('<p>')
        h.append(_("Once signed, this document cannot be edited or tampered with.", l))
        h.append('</p>')
    h.append("</body></html>")
    return "\n".join(h)

def page_messages(l, homelink, mess):
    h = []
    h.append(jqm_page_header("messages", _("Messages", l), homelink))
    h.append(jqm_button("#addmessage", _("Add Message", l), "plus"))
    hm = []
    for m in mess:
        icon = "info"
        if m["PRIORITY"] == 1:
            icon = "alert"
        inner = jqm_h3(python2display(l, m["ADDED"]) + " " + m["CREATEDBY"])
        inner += jqm_p(m["MESSAGE"])
        hm.append(jqm_collapsible(inner, icon))
    h.append(jqm_collapsible_set("\n".join(hm)))
    h.append(jqm_page_footer())
    return h

def page_message_add(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("addmessage", _("Add Message", l), homelink))
    h.append(jqm_form("messageform"))
    h.append(jqm_hidden("posttype", "message"))
    h.append(jqm_fieldcontain("forname", _("For", l), jqm_select("forname", html.options_users_and_roles(dbo, False, True))))
    h.append(jqm_fieldcontain("expires", _("Expires", l), jqm_select("expires", jqm_options_next_month(l))))
    h.append(jqm_fieldcontain("priority", _("Priority", l), jqm_select("priority", 
        jqm_option("0", _("Information", l), True) + jqm_option("1", _("Important", l), False))))
    h.append(jqm_fieldcontain("email", _("Send via email", l), jqm_checkbox("email", configuration.email_messages(dbo))))
    h.append(jqm_fieldcontain("message", _("Note", l), jqm_text("message")))
    h.append(jqm_submit(_("Add Message", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_reports(l, homelink, ar):
    h = []
    h.append(jqm_page_header("reports", _("Reports", l), homelink))
    rs = []
    group = ""
    for r in ar:
        if group != r["CATEGORY"]:
            group = r["CATEGORY"]
            rs.append(jqm_list_divider(group))
        rs.append(jqm_listitem_link("mobile_report?id=%d" % r["ID"], r["TITLE"], "report"))
    h.append(jqm_list("\n".join(rs), True))
    h.append(jqm_page_footer())
    return h

def page_vaccinations(l, homelink, vacc):
    h = []
    h.append(jqm_page_header("vacc", _("Vaccinate", l), homelink))
    group = ""
    vlist = []
    vforms = []
    for v in vacc:
        required = python2display(l, v["DATEREQUIRED"])
        if group != required:
            group = required
            vlist.append(jqm_list_divider(group))
        pageid = "v" + str(v["ID"])
        vlist.append(jqm_listitem_link("#" + pageid, 
            "%s - %s (%s)" % (v["ANIMALNAME"], v["SHELTERCODE"], v["VACCINATIONTYPE"]),
            "vaccination", -1, ""))
        vforms.append(jqm_page_header(pageid, v["VACCINATIONTYPE"], homelink))
        vforms.append(jqm_table())
        vforms.append(jqm_tablerow( _("Animal", l), 
            jqm_link("mobile_post?posttype=va&id=%d" % v["ANIMALID"], v["SHELTERCODE"] + " " + v["ANIMALNAME"])))
        vforms.append(jqm_tablerow( _("Vaccination", l), required + " " + v["VACCINATIONTYPE"]))
        vforms.append(jqm_tablerow( _("Comments", l), v["COMMENTS"]))
        vforms.append(jqm_table_end())
        vforms.append(jqm_button("mobile_post?posttype=vacc&id=%s&animalid=%s" % (str(v["ID"]), str(v["ANIMALID"])), _("Vaccinate", l), "check"))
        vforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(vlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(vforms))
    return h

def page_tests(l, homelink, test, testresults):
    h = []
    h.append(jqm_page_header("test", _("Test", l), homelink))
    group = ""
    tlist = []
    tforms = []
    for t in test:
        required = python2display(l, t["DATEREQUIRED"])
        if group != required:
            group = required
            tlist.append(jqm_list_divider(group))
        pageid = "t" + str(t["ID"])
        tlist.append(jqm_listitem_link("#" + pageid, 
            "%s - %s (%s)" % (t["ANIMALNAME"], t["SHELTERCODE"], t["TESTNAME"]),
            "vaccination", -1, ""))
        tforms.append(jqm_page_header(pageid, t["TESTNAME"], homelink))
        tforms.append(jqm_table())
        tforms.append(jqm_tablerow( _("Animal", l), 
            jqm_link("mobile_post?posttype=va&id=%d" % t["ANIMALID"], t["SHELTERCODE"] + " " + t["ANIMALNAME"])))
        tforms.append(jqm_tablerow( _("Test", l), required + " " + t["TESTNAME"]))
        tforms.append(jqm_tablerow( _("Comments", l), t["COMMENTS"]))
        tforms.append(jqm_table_end())
        tforms.append(jqm_p(_("Result", l) + ": " + 
            "<select class=\"testresult\" data=\"%s\" data-animal=\"%s\">" % (str(t["ID"]), t["ANIMALID"]) +
            "<option value=""></option>" + 
            jqm_options(testresults, "ID", "RESULTNAME") + "</select>"))
        tforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(tlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(tforms))
    return h

def page_medication(l, homelink, med):
    h = []
    h.append(jqm_page_header("med", _("Medicate", l), homelink))
    group = ""
    mlist = []
    mforms = []
    for m in med:
        required = python2display(l, m["DATEREQUIRED"])
        if group != required:
            group = required
            mlist.append(jqm_list_divider(group))
        pageid = "m" + str(m["TREATMENTID"])
        mlist.append(jqm_listitem_link("#" + pageid,
            "%s - %s (%s)" % (m["ANIMALNAME"], m["SHELTERCODE"], m["TREATMENTNAME"]),
            "medical", -1, ""))
        mforms.append(jqm_page_header(pageid, m["TREATMENTNAME"], homelink))
        mforms.append(jqm_table());
        mforms.append(jqm_tablerow(_("Animal", l),
            jqm_link("mobile_post?posttype=va&id=%d" % m["ANIMALID"], m["SHELTERCODE"] + " " + m["ANIMALNAME"])))
        mforms.append(jqm_tablerow(_("Treatment", l), "%s %s<br />%s" % (required, m["TREATMENTNAME"], m["DOSAGE"])))
        mforms.append(jqm_tablerow(_("Comments", l), m["COMMENTS"]))
        mforms.append(jqm_table_end())
        mforms.append(jqm_button("mobile_post?posttype=med&id=%s&animalid=%s&medicalid=%s" % 
            (str(m["TREATMENTID"]), str(m["ANIMALID"]), str(m["REGIMENID"])), _("Medicate", l), "check"))
        mforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(mlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(mforms))
    return h

def page_check_licence(l, homelink):
    h = []
    h.append(jqm_page_header("checklicence", _("Check License", l), homelink))
    h.append(jqm_form("licenceform"))
    h.append(jqm_hidden("posttype", "lc"))
    h.append(jqm_fieldcontain("licence", _("License Number", l), jqm_text("licence")))
    h.append(jqm_submit(_("Check", l)))
    h.append(jqm_page_footer())
    return h

def page_diary(l, homelink, dia):
    h = []
    h.append(jqm_page_header("diary", _("Diary", l), homelink))
    group = ""
    dlist = []
    dforms = []
    for d in dia:
        fordate = python2display(l, d["DIARYDATETIME"])
        if group != fordate:
            group = fordate
            dlist.append(jqm_list_divider(group))
        pageid = "d" + str(d["ID"])
        dlist.append(jqm_listitem_link("#" + pageid,
            "%s (%s)" % (d["SUBJECT"], d["LINKINFO"]),
            "diary", -1, ""))
        dforms.append(jqm_page_header(pageid, d["SUBJECT"], homelink))
        dforms.append(jqm_table());
        dforms.append(jqm_tablerow(_("Subject", l), d["SUBJECT"]))
        lt = d["LINKINFO"]
        if d["LINKTYPE"] == diary.ANIMAL:
            lt = jqm_link("mobile_post?posttype=va&id=%d" % d["LINKID"], d["LINKINFO"])
        dforms.append(jqm_tablerow(_("Link", l), lt))
        dforms.append(jqm_tablerow(_("Note", l), d["NOTE"]))
        dforms.append(jqm_table_end())
        dforms.append(jqm_button("mobile_post?posttype=dia&on=0&id=%s" % str(d["ID"]), _("Complete", l), "check"))
        dforms.append(jqm_p(_("Or move this diary on to", l) + ": " + 
            "<select class=\"diaryon\" data=\"%s\">" % str(d["ID"]) +
            jqm_options_next_month(l) + "</select>"))
        dforms.append(jqm_page_footer())
    h.append(jqm_list("\n".join(dlist), True))
    h.append(jqm_page_footer())
    h.append("\n".join(dforms))
    return h

def page_diary_add(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("diaryadd", _("Add Diary", l), homelink))
    h.append(jqm_form("diaryform"))
    h.append(jqm_hidden("posttype", "dianew"))
    h.append(jqm_fieldcontain("diaryfor", _("For", l), jqm_select("diaryfor", html.options_users_and_roles(dbo))))
    h.append(jqm_fieldcontain("diarydate", _("Date", l), jqm_select("diarydate", jqm_options_next_month(l))))
    h.append(jqm_fieldcontain("subject", _("Subject", l), jqm_text("subject")))
    h.append(jqm_fieldcontain("note", _("Note", l), jqm_text("note")))
    h.append(jqm_submit(_("Add Diary", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_log_add(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("log", _("Add Log", l), homelink))
    h.append(jqm_form("logform"))
    h.append(jqm_hidden("posttype", "log"))
    h.append(jqm_fieldcontain("animalid", _("Animal", l), jqm_select("animalid", html.options_animals_on_shelter(dbo))))
    h.append(jqm_fieldcontain("logtypeid", _("Log Type", l), jqm_select("logtypeid", html.options_log_types(dbo))))
    h.append(jqm_fieldcontain("logtext", _("Log Text", l), jqm_text("logtext")))
    h.append(jqm_submit(_("Add Log", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_homecheck(l, homelink, dbo):
    h = []
    h.append(jqm_page_header("homecheck", _("Perform Homecheck", l), homelink))
    h.append(jqm_form("hcform"))
    h.append(jqm_hidden("posttype", "hc"))
    h.append(jqm_fieldcontain("personid", _("Person", l), jqm_select("personid", html.options_people_not_homechecked(dbo))))
    h.append(jqm_fieldcontain("comments", _("Comments", l), jqm_text("comments")))
    h.append(jqm_submit(_("Pass Homecheck", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    return h

def page_stocklevels(l, homelink, stl):
    h = []
    h.append(jqm_page_header("stl", _("Stock Take", l), homelink))
    vlist = []
    for s in stl:
        vlist.append(jqm_listitem_link("mobile_post?posttype=st&id=%s" % s["ID"], s["LOCATIONNAME"], "stock", s["TOTAL"]))
    h.append(jqm_list("\n".join(vlist), True))
    h.append(jqm_page_footer())
    return h

def page_incidents(l, homelink, inc, pageid = "inmy", pagetitle = ""):
    h = []
    h.append(jqm_page_header(pageid, pagetitle, homelink))
    vlist = []
    for i in inc:
        vlist.append(jqm_listitem_link("mobile_post?posttype=vinc&id=%s" % i["ID"], 
            "%s: %s - %s" % (python2display(l, i["INCIDENTDATETIME"]), i["INCIDENTNAME"], i["DISPATCHADDRESS"]), "call"))
    h.append(jqm_list("\n".join(vlist), True))
    h.append(jqm_page_footer())
    return h

def page_login(l, post):
    accountline = ""
    accounttext = _("Database", l)
    if smcom.active(): accounttext = _("SM Account", l)
    if MULTIPLE_DATABASES:
        accountline = "<div data-role='fieldcontain'><label for='database'>%s</label><input type='text' id='database' name='database' value='%s'/></div>" % (accounttext, html.escape(post["smaccount"]))
    return header(l) + """
        <div data-role='page' id='login'>
        <div data-role='header'>
        <h1>%s</h1>
        </div>
        <div data-role='content'>
        <form id="loginform" action="mobile_login" target="_self" method="post">
        <h2>%s</h2>
        %s
        <div data-role="fieldcontain">
            <label for="username">%s</label>
            <input type="text" id="username" name="username" value='%s' />
        </div>
        <div data-role="fieldcontain">
            <label for="password">%s</label>
            <input type="password" id="password" name="password" value='%s' />
        </div>
        <button type="submit">%s</button>
        </form>
        </div>
        </div>
        </body>
        </html>
    """ % ( _("Login", l), _("Login", l), accountline, 
        _("Username", l), html.escape(post["username"]), 
        _("Password", l), html.escape(post["password"]),
        _("Login", l) )

def handler(dbo, user, locationfilter, post):
    """
    Handles posts from the frontend. Depending on the type we either
    return more HTML for the javascript to inject, or GO URL to have
    the controller redirect to URL
    """
    l = dbo.locale
    homelink = "<a href='mobile' data-ajax='false' class='ui-btn-right' data-icon='home' data-theme='b'>%s</a>" % _("Home", l)
    mode = post["posttype"]
    pid = post.integer("id")
    animalid = post.integer("animalid")

    if mode == "vacc":
        # We're vaccinating an animal
        a = animal.get_animal(dbo, animalid)
        medical.update_vaccination_today(dbo, user, pid)
        return jqm_page_header("", _("Vaccination Given", l), homelink) + \
            jqm_p(_("Vaccination marked as given for {0} - {1}", l).format(a["ANIMALNAME"], a["SHELTERCODE"])) + \
            jqm_button("mobile#vacc", _("More Vaccinations", l), "", "false") + \
            jqm_page_footer()

    if mode == "test":
        # We're performing a test on an animal
        a = animal.get_animal(dbo, animalid)
        medical.update_test_today(dbo, user, pid, post.integer("resultid"))
        return jqm_page_header("", _("Test Performed", l), homelink) + \
            jqm_p(_("Test marked as performed for {0} - {1}", l).format(a["ANIMALNAME"], a["SHELTERCODE"])) + \
            jqm_button("mobile#test", _("More Tests", l), "", "false") + \
            jqm_page_footer()

    elif mode == "med":
        # We're treating an animal
        a = animal.get_animal(dbo, animalid)
        medical.update_treatment_today(dbo, user, pid)
        return jqm_page_header("", _("Treatment Given", l), homelink) + \
            jqm_p(_("Treatment marked as given for {0} - {1}", l).format(a["ANIMALNAME"], a["SHELTERCODE"])) + \
            jqm_button("mobile#med", _("More Medications", l), "", "false") + \
            jqm_page_footer()

    elif mode == "dia":
        # We're completing a diary task
        d = diary.get_diary(dbo, pid)
        if post["on"] == "0":
            diary.complete_diary_note(dbo, user, pid)
            return jqm_page_header("", _("Completed", l), homelink) + \
                jqm_p(_("Diary note {0} marked completed", l).format(d["SUBJECT"])) + \
                jqm_button("mobile#diary", _("More diary notes", l), "", "false") + \
                jqm_page_footer()
        else:
            diary.rediarise_diary_note(dbo, user, pid, post.date("on"))
            return jqm_page_header("", _("Rediarised", l), homelink) + \
                jqm_p(_("Diary note {0} rediarised for {1}", l).format(d["SUBJECT"], post["on"])) + \
                jqm_button("mobile#diary", _("More diary notes", l), "", "false") + \
                jqm_page_footer()

    elif mode == "dianew":
        # We're adding a diary note
        diary.insert_diary(dbo, user, 0, 0, post.date("diarydate"), 
            post["diaryfor"], post["subject"], post["note"])
        return "GO mobile"

    elif mode == "message":
        # We're adding a message
        lookups.add_message(dbo, user, post.boolean("email"), post["message"], post["forname"], post.integer("priority"), post.date("expires"))
        return "GO mobile"

    elif mode == "log":
        # We're adding a log to an animal
        a = animal.get_animal(dbo, animalid)
        log.add_log(dbo, user, log.ANIMAL, animalid, post.integer("logtypeid"), post["logtext"])
        return "GO mobile"

    elif mode == "hc":
        # We're marking an owner homechecked
        person.update_pass_homecheck(dbo, user, post.integer("personid"), post["comments"])
        return "GO mobile"

    elif mode == "vsa":
        # Return a list of the shelter animals
        h = []
        alin = []
        h.append(header(l))
        h.append(jqm_page_header("", _("Shelter Animals", l), homelink))
        an = animal.get_animal_find_simple(dbo, "", "all", 0, locationfilter)
        for a in an:
            alin.append(jqm_listitem_link("mobile_post?posttype=va&id=%d" % a["ID"],
                "%s - %s (%s %s %s) %s" % (a["CODE"], a["ANIMALNAME"], a["SEXNAME"], a["BREEDNAME"], a["SPECIESNAME"], a["IDENTICHIPNUMBER"]),
                "animal"))
        h.append(jqm_list("\n".join(alin), True))
        h.append(jqm_page_footer())
        h.append("</body></html>")
        return "\n".join(h)

    elif mode == "uai":
        # Upload an animal image
        media.attach_file_from_form(dbo, user, media.ANIMAL, animalid, post)
        return "GO mobile_post?posttype=va&id=%d&success=true" % animalid

    elif mode == "aas":
        return handler_addanimal(l, homelink, dbo)

    elif mode == "aa":
        nid, ncode = animal.insert_animal_from_form(dbo, post, user)
        return "GO mobile_post?posttype=va&id=%d" % nid

    elif mode == "aincs":
        return handler_addincident(l, homelink, dbo)

    elif mode == "ainc":
        post.data["incidentdate"] = python2display(l, now(dbo.timezone))
        post.data["incidenttime"] = format_time(now(dbo.timezone))
        post.data["calldate"] = post.data["incidentdate"]
        post.data["calltime"] = post.data["incidenttime"]
        post.data["calltaker"] = user
        nid = animalcontrol.insert_animalcontrol_from_form(dbo, post, user)
        return "GO mobile_post?posttype=vinc&id=%d" % nid

    elif mode == "lc":
        q = post["licence"]
        matches = []
        if q.strip() != "": matches = financial.get_licence_find_simple(dbo, q)
        return handler_check_licence(l, homelink, q, matches)

    elif mode == "va":
        # Display a page containing the selected animal by id
        a = animal.get_animal(dbo, pid)
        af = additional.get_additional_fields(dbo, pid, "animal")
        diet = animal.get_diets(dbo, pid)
        vacc = medical.get_vaccinations(dbo, pid)
        test = medical.get_tests(dbo, pid)
        med = medical.get_regimens(dbo, pid)
        logs = log.get_logs(dbo, log.ANIMAL, pid)
        return handler_viewanimal(l, dbo, a, af, diet, vacc, test, med, logs, homelink, post)

    elif mode == "vinc":
        # Display a page containing the selected incident by id
        a = animalcontrol.get_animalcontrol(dbo, pid)
        amls = animalcontrol.get_animalcontrol_animals(dbo, pid)
        cit = financial.get_incident_citations(dbo, pid)
        dia = diary.get_diaries(dbo, diary.ANIMALCONTROL, pid)
        logs = log.get_logs(dbo, log.ANIMALCONTROL, pid)
        return handler_viewincident(l, dbo, a, amls, cit, dia, logs, homelink, post)

    elif mode == "vinccomp":
        # Mark the incident with pid completed with type=ct
        animalcontrol.update_animalcontrol_completenow(dbo, pid, user, post.integer("ct"))
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "vincdisp":
        # Mark the incident with id dispatched now with the current user as aco
        animalcontrol.update_animalcontrol_dispatchnow(dbo, pid, user)
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "vincresp":
        # Mark the incident with id responded to now
        animalcontrol.update_animalcontrol_respondnow(dbo, pid, user)
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "vinclog":
        # Add a log to the incident of id with logtype and logtext
        log.add_log(dbo, user, log.ANIMALCONTROL, pid, post.integer("logtype"), post["logtext"])
        return "GO mobile_post?posttype=vinc&id=%d" % pid

    elif mode == "st":
        # Display a page to adjust stock levels for id
        sl = stock.get_stocklevels(dbo, pid)
        return handler_stocklocation(l, homelink, lookups.get_stock_location_name(dbo, pid), sl)

    elif mode == "stu":
        # Update the stock levels from the posted values
        stock.stock_take_from_mobile_form(dbo, user, post)
        return "GO mobile"

    elif mode == "sign":
        # We're electronically signing a document
        for mid in post.integer_list("ids"):
            media.sign_document(dbo, user, mid, post["sig"], post["signdate"])
            configuration.signpad_ids(dbo, user, " ")
        return "ok"

def handler_addanimal(l, homelink, dbo):
    h = []
    h.append(header(l))
    h.append(jqm_page_header("animaladd", _("Add Animal", l), homelink))
    h.append(jqm_form("animalform"))
    h.append(jqm_hidden("posttype", "aa"))
    h.append(jqm_fieldcontain("animalname", _("Name", l), jqm_text("animalname")))
    h.append(jqm_fieldcontain("estimatedage", _("Age", l), jqm_text("estimatedage", "1.0")))
    h.append(jqm_fieldcontain("sex", _("Sex", l), jqm_select("sex", html.options_sexes(dbo))))
    h.append(jqm_fieldcontain("animaltype", _("Type", l), jqm_select("animaltype", html.options_animal_types(dbo, False, configuration.default_type(dbo)))))
    h.append(jqm_fieldcontain("species", _("Species", l), jqm_select("species", html.options_species(dbo, False, configuration.default_species(dbo)))))
    h.append(jqm_fieldcontain("breed1", _("Breed", l), jqm_select("breed1", html.options_breeds(dbo, False, configuration.default_breed(dbo)))))
    h.append(jqm_fieldcontain("basecolour", _("Color", l), jqm_select("basecolour", html.options_colours(dbo, False, configuration.default_colour(dbo)))))
    h.append(jqm_fieldcontain("internallocation", _("Location", l), jqm_select("internallocation", html.options_internal_locations(dbo, False, configuration.default_location(dbo)))))
    h.append(jqm_fieldcontain("unit", _("Unit", l), jqm_text("unit")))
    h.append(jqm_fieldcontain("size", _("Size", l), jqm_select("size", html.options_sizes(dbo, False, configuration.default_size(dbo)))))
    h.append(jqm_submit(_("Add Animal", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_addincident(l, homelink, dbo):
    h = []
    h.append(header(l))
    h.append(jqm_page_header("incidentadd", _("Add Call", l), homelink))
    h.append(jqm_form("incform"))
    h.append(jqm_hidden("posttype", "ainc"))
    h.append(jqm_fieldcontain("incidenttype", _("Type", l), jqm_select("incidenttype", html.options_incident_types(dbo, False, configuration.default_incident(dbo)))))
    h.append(jqm_fieldcontain("callnotes", _("Notes", l), jqm_text("callnotes")))
    h.append(jqm_fieldcontain("dispatchaddress", _("Address", l), jqm_text("dispatchaddress")))
    h.append(jqm_fieldcontain("dispatchtown", _("City", l), jqm_text("dispatchtown")))
    h.append(jqm_fieldcontain("dispatchcounty", _("State", l), jqm_text("dispatchcounty")))
    h.append(jqm_fieldcontain("dispatchpostcode", _("Zipcode", l), jqm_text("dispatchpostcode")))
    h.append(jqm_submit(_("Add", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_check_licence(l, homelink, q, matches):
    """
    Generates the page of results of matching licences.
    l: The locale
    matches: A list of licence records from get_licence_find_simple
    """
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", _("Results for '{0}'.", l).format(q), homelink))
    for m in matches:
        h.append("<p><b>%s (%s) - %s</b>" % (m["LICENCENUMBER"], m["LICENCETYPENAME"], m["OWNERNAME"]))
        if m["OWNERADDRESS"] is not None and m["OWNERADDRESS"].strip() != "":
            h.append("<br/>%s, %s, %s %s" % (m["OWNERADDRESS"], m["OWNERTOWN"], m["OWNERCOUNTY"], m["OWNERPOSTCODE"]))
        h.append("<br/>%s %s %s" % (python2display(l, m["ISSUEDATE"]), html.icon("right"), python2display(l, m["EXPIRYDATE"])))
        if m["SHELTERCODE"] is not None: 
            h.append("<br/>%s %s" % (m["SHELTERCODE"], m["ANIMALNAME"]))
        if len(m["COMMENTS"]) != 0: 
            h.append("<br/>%s" % m["COMMENTS"])
        h.append("</p>")
    if q.strip() == "":
        h.append("<p>%s</p>" % _("No data.", l))
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_viewanimal(l, dbo, a, af, diet, vacc, test, med, logs, homelink, post):
    """
    Generate the view animal mobile page.
    l:  The locale
    a:  An animal record
    af: Additional fields for the animal record
    diet: Diets for the animal
    vacc: Vaccinations for the animal
    test: Tests for the animal
    med: Medicals for the animal
    logs: Logs for the animal
    homelink: Link to the home menu
    post: The posted values
    """
    def table():
        return "<table style='width: 100%; border-bottom: 1px solid black;'>"
    def table_end():
        return "</table>"
    def hd(label):
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td></tr>" % label
    def tr(label, value, value2 = "", value3 = ""):
        if value is None or str(value).startswith("None "): value = ""
        if value2 is None or str(value2).startswith("None"): value2 = ""
        if value2 is not None and value2 != "": value2 = "<td>%s</td>" % value2
        if value3 is not None and value3 != "": value3 = "<td>%s</td>" % value3
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td><td>%s</td>%s%s</tr>" % (label, value, value2, value3)
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", "%s - %s" % (a["CODE"], a["ANIMALNAME"]), homelink))
    h.append(table())
    h.append("<tr><td><img src='%s' class='asm-thumbnail' /></td>" % html.thumbnail_img_src(a, "animalthumb"))
    h.append("<td><h2 style='margin: 2px;'>%s - %s</h2>" % (a["CODE"], a["ANIMALNAME"]))
    h.append("%s %s %s</td>" % (a["SEXNAME"], a["BREEDNAME"], a["SPECIESNAME"]))
    h.append("</tr></table>")
    h.append(table())
    uploadstatus = ""
    if post["success"] == "true":
        uploadstatus = _("Photo successfully uploaded.", l)
    h.append("""
        <tr><td style='font-weight: bold; width: 150px;'>%s</td>
        <td>
        <form data-ajax="false" action="mobile_post" method="post" enctype="multipart/form-data">
        <input type="hidden" name="animalid" value="%d" />
        <input type="hidden" name="posttype" value="uai" />
        <input type="hidden" name="comments" value="" />
        <input type="hidden" name="base64image" value="" />
        <input type="file" data-role='none' accept="image/*" capture="camera" name="filechooser" id="fc%d" />
        <span class=".tipios6" style="display: none">%s</span>
        <input id='sfc%d' type='submit' data-icon='arrow-u' data-inline='true' data-mini='true' value='%s' />
        </form>
        <span class="tip">%s</span>
        </td></tr>""" % (_("Upload Photo", l), a["ID"], a["ID"], 
                        _("You will need to upgrade to iOS 6 or higher to upload files.", l),
                         a["ID"], _("Send", l), uploadstatus))
    h.append(table_end())
    h.append("""
    <script type="text/javascript">
        // If this is an idevice and the file upload box is
        // disabled, it needs upgrading to iOS6 or better.
        if (is_idevice && $("#fc%d").attr("disabled")) {
            $(".tipios6").show();
        }
    </script>
    """ % ( a["ID"] ))
    h.append(table())
    h.append(tr( _("Type", l), a["ANIMALTYPENAME"]))
    h.append(tr( _("Location", l), a["DISPLAYLOCATIONNAME"]))
    h.append(tr( _("Color", l), a["BASECOLOURNAME"]))
    h.append(tr( _("Coat Type", l), a["COATTYPENAME"]))
    h.append(tr( _("Size", l), a["SIZENAME"]))
    h.append(tr( _("DOB", l), python2display(l, a["DATEOFBIRTH"]), a["ANIMALAGE"]))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Markings", l), a["MARKINGS"]))
    h.append(tr( _("Hidden Comments", l), a["HIDDENANIMALDETAILS"]))
    h.append(tr( _("Comments", l), a["ANIMALCOMMENTS"]))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Cats", l), a["ISGOODWITHCATSNAME"]))
    h.append(tr( _("Dogs", l), a["ISGOODWITHDOGSNAME"]))
    h.append(tr( _("Children", l), a["ISGOODWITHCHILDRENNAME"]))
    h.append(tr( _("Housetrained", l), a["ISHOUSETRAINEDNAME"]))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Original Owner", l), a["ORIGINALOWNERNAME"]))
    h.append(tr( _("Brought In By", l), a["BROUGHTINBYOWNERNAME"]))
    h.append(tr( _("Date Brought In", l), python2display(l, a["DATEBROUGHTIN"])))
    h.append(tr( _("Bonded With", l), "%s %s %s %s" % (a["BONDEDANIMAL1CODE"], a["BONDEDANIMAL1NAME"], a["BONDEDANIMAL2CODE"], a["BONDEDANIMAL2NAME"])))
    h.append(tr( _("Transfer?", l), a["ISTRANSFERNAME"] == 1))
    h.append(tr( _("Entry Category", l), a["ENTRYREASONNAME"]))
    h.append(tr( _("Entry Reason", l), a["REASONFORENTRY"]))
    h.append(table_end())
    h.append(table())
    h.append(tr( _("Microchipped", l), python2display(l, a["IDENTICHIPDATE"]), a["IDENTICHIPNUMBER"]))
    h.append(tr( _("Tattoo", l), python2display(l, a["TATTOODATE"]), a["TATTOONUMBER"]))
    h.append(tr( _("Neutered", l), python2display(l, a["NEUTEREDDATE"])))
    h.append(tr( _("Declawed", l), a["DECLAWEDNAME"]))
    h.append(tr( _("Heartworm Tested", l), python2display(l, a["HEARTWORMTESTDATE"]), a["HEARTWORMTESTRESULTNAME"]))
    h.append(tr( _("FIV/L Tested", l), python2display(l, a["COMBITESTDATE"]), "%s %s" % (a["COMBITESTRESULTNAME"], a["FLVRESULTNAME"])))
    h.append(tr( _("Health Problems", l), a["HEALTHPROBLEMS"]))
    h.append(tr( _("Rabies Tag", l), a["RABIESTAG"]))
    h.append(tr( _("Special Needs", l), a["HASSPECIALNEEDSNAME"]))
    h.append(tr( _("Current Vet", l), a["CURRENTVETNAME"], a["CURRENTVETWORKTELEPHONE"]))
    h.append(table_end())
    
    if len(af) > 0:
        h.append(table())
        for d in af:
            if d["FIELDTYPE"] == additional.ANIMAL_LOOKUP:
                h.append(tr(d["FIELDLABEL"], animal.get_animal_namecode(dbo, utils.cint(d["VALUE"]))))
            elif d["FIELDTYPE"] == additional.PERSON_LOOKUP:
                h.append(tr(d["FIELDLABEL"], person.get_person_name_code(dbo, utils.cint(d["VALUE"]))))
            elif d["FIELDTYPE"] == additional.MONEY:
                h.append(tr(d["FIELDLABEL"], format_currency(l, d["VALUE"])))
            elif d["FIELDTYPE"] == additional.YESNO:
                h.append(tr(d["FIELDLABEL"], d["VALUE"] == "1" and _("Yes", l) or _("No", l)))
            else:
                h.append(tr(d["FIELDLABEL"], d["VALUE"]))
        h.append(table_end())
    
    h.append(table())
    h.append(hd(_("Diet", l)))
    for d in diet:
        h.append(tr(python2display(l, d["DATESTARTED"]), d["DIETNAME"], d["COMMENTS"]))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Vaccination", l)))
    for v in vacc:
        h.append(tr(python2display(l, v["DATEREQUIRED"]), python2display(l, v["DATEOFVACCINATION"]), v["VACCINATIONTYPE"]))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Test", l)))
    for t in test:
        h.append(tr(python2display(l, t["DATEREQUIRED"]), python2display(l, t["DATEOFTEST"]), t["TESTNAME"], t["RESULTNAME"]))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Medical", l)))
    for m in med:
        h.append(tr(python2display(l, m["STARTDATE"]), m["TREATMENTNAME"], m["DOSAGE"]))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Log", l)))
    for lo in logs:
        h.append(tr(python2display(l, lo["DATE"]), lo["LOGTYPENAME"], lo["COMMENTS"]))
    h.append(table_end())
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_viewincident(l, dbo, a, amls, cit, dia, logs, homelink, post):
    """
    Generate the view incident mobile page.
    l:  The locale
    a:   An incident record
    amls: Any linked animals for the incident
    cit: Citations for the incident
    dia: Diary notes for the incident
    logs: Logs for the incident
    homelink: Link to the home menu
    post: The posted values
    """
    dummy = post # TODO remove if used
    def table():
        return "<table style='width: 100%; border-bottom: 1px solid black;'>"
    def table_end():
        return "</table>"
    def hd(label):
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td></tr>" % label
    def tr(label, value, value2 = "", value3 = ""):
        if value is None or str(value).startswith("None "): value = ""
        if value2 is None or str(value2).startswith("None"): value2 = ""
        if value2 is not None and value2 != "": value2 = "<td>%s</td>" % value2
        if value3 is not None and value3 != "": value3 = "<td>%s</td>" % value3
        return "<tr><td style='font-weight: bold; width: 150px'>%s</td><td>%s</td>%s%s</tr>" % (label, value, value2, value3)
    def dt(field):
        if field is None: return ""
        return "%s %s" % (python2display(l, field), format_time(field))
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", "%s - %s" % (a["INCIDENTNAME"], a["OWNERNAME"]), homelink))
    h.append(table())
    h.append("<tr>")
    h.append("<td><h2 style='margin: 2px;'>%s - %s</h2>" % (a["INCIDENTNAME"], a["OWNERNAME"]))
    h.append("%s</td>" % (a["CALLNOTES"]))
    h.append("</tr></table>")
    h.append(table())
    h.append(tr( _("Number", l), utils.padleft(a["ID"], 6)))
    h.append(tr( _("Type", l), a["INCIDENTNAME"]))
    h.append(tr( _("Incident Date/Time", l), dt(a["INCIDENTDATETIME"])))
    h.append(tr( _("Notes", l), a["CALLNOTES"]))
    h.append(tr( _("Completion Date", l), python2display(l, a["COMPLETEDDATE"])))
    comptp = a["COMPLETEDNAME"]
    if a["COMPLETEDDATE"] is None:
        comptp = jqm_select("comptype", 
            '<option value="-1"></option>' + jqm_options(lookups.get_incident_completed_types(dbo), "ID", "COMPLETEDNAME"), 
            "completedtype", str(a["ID"]))
    h.append(tr( _("Completion Type", l), comptp))
    h.append(tr( _("Call Date/Time", l), dt(a["CALLDATETIME"])))
    h.append(tr( _("Taken By", l), a["CALLTAKER"]))
    h.append(tr( _("Caller", l), a["CALLERNAME"]))
    h.append(tr( _("Victim", l), a["VICTIMNAME"]))
    h.append(table_end())
   
    h.append(table())
    h.append(hd(_("Dispatch", l)))
    h.append(tr( _("Address", l), a["DISPATCHADDRESS"]))
    h.append(tr( _("City", l), a["DISPATCHTOWN"]))
    h.append(tr( _("State", l), a["DISPATCHCOUNTY"]))
    h.append(tr( _("Zipcode", l), a["DISPATCHPOSTCODE"]))
    h.append(tr( _("Dispatched ACO", l), a["DISPATCHEDACO"]))
    dispdt = dt(a["DISPATCHDATETIME"])
    if dispdt == "":
        dispdt = jqm_button("mobile_post?posttype=vincdisp&id=%d" % a["ID"], _("Dispatch", l), "calendar", "false")
    h.append(tr( _("Dispatch Date/Time", l), dispdt))
    respdt = dt(a["RESPONDEDDATETIME"])
    if respdt == "":
        respdt = jqm_button("mobile_post?posttype=vincresp&id=%d" % a["ID"], _("Respond", l), "calendar", "false")
    # If it's not dispatched yet, don't allow respond
    if a["DISPATCHDATETIME"] is None: respdt = ""
    h.append(tr( _("Responded Date/Time", l), respdt))
    h.append(tr( _("Followup Date/Time", l), dt(a["FOLLOWUPDATETIME"])))
    h.append(tr( _("Followup Date/Time", l), dt(a["FOLLOWUPDATETIME2"])))
    h.append(tr( _("Followup Date/Time", l), dt(a["FOLLOWUPDATETIME3"])))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Suspect/Animal", l)))
    h.append(tr( _("Suspect 1", l), a["OWNERNAME1"]))
    h.append(tr( _("Suspect 2", l), a["OWNERNAME2"]))
    h.append(tr( _("Suspect 3", l), a["OWNERNAME3"]))
    for m in amls:
        h.append(tr( _("Animal", l), '<a href="mobile_post?posttype=va&id=%d">%s - %s</a>' % (m["ANIMALID"], m["SHELTERCODE"], m["ANIMALNAME"])))
    h.append(tr( _("Species", l), a["SPECIESNAME"]))
    h.append(tr( _("Sex", l), a["SEXNAME"]))
    h.append(tr( _("Age Group", l), a["AGEGROUP"]))
    h.append(tr( _("Description", l), a["ANIMALDESCRIPTION"]))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Citations", l)))
    for c in cit:
        h.append(tr(python2display(l, c["CITATIONDATE"]), c["CITATIONNAME"], c["COMMENTS"]))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Diary", l)))
    for d in dia:
        h.append(tr(python2display(l, d["DIARYDATETIME"]), d["SUBJECT"], d["NOTE"]))
    h.append(table_end())

    h.append(table())
    h.append(hd(_("Log", l)))
    for lo in logs:
        h.append(tr(python2display(l, lo["DATE"]), lo["LOGTYPENAME"], lo["COMMENTS"]))
    h.append(table_end())

    h.append(jqm_form("aclog", ajax="false"))
    h.append(jqm_hidden("id", str(a["ID"])))
    h.append(jqm_hidden("posttype", "vinclog"))
    h.append(jqm_fieldcontain("logtype", _("Log Type", l), jqm_select("logtype", jqm_options(lookups.get_log_types(dbo), "ID", "LOGTYPENAME"))))
    h.append(jqm_fieldcontain("logtext", _("Log Text", l), jqm_text("logtext")))
    h.append(jqm_submit(_("Add Log", l)))
    h.append(jqm_form_end())

    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def handler_stocklocation(l, homelink, locationname, sl):
    """
    Generate a page that allows adjusting stock levels in the 
    records sl
    """
    h = []
    h.append(header(l))
    h.append(jqm_page_header("", locationname, homelink))
    h.append(jqm_form("st"))
    h.append(jqm_hidden("posttype", "stu"))
    for s in sl:
        h.append(jqm_fieldcontain("sl%d" % s["SLID"], s["NAME"], jqm_slider("sl%d" % s["SLID"], 0, s["TOTAL"], s["BALANCE"])))
    h.append(jqm_submit(_("Save", l)))
    h.append(jqm_form_end())
    h.append(jqm_page_footer())
    h.append("</body></html>")
    return "\n".join(h)

def login(post, session, remoteip, path):
    """
    Handles the login post
    """
    url = users.web_login(post, session, remoteip, path)
    if url == "FAIL" or url == "DISABLED":
        return "mobile_login"
    else:
        return "mobile"

def report(dbo, crid, user):
    """
    Generates a report for mobile devices. 
    crid: The custom report id
    user: The username of the user running the report
    """
    return reports.execute(dbo, crid, user)

