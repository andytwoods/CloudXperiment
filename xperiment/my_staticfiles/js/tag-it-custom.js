/**
 * jQuery tagit without use jQuery UI javascript, but use the jQuery UI css style.
 *
 * use eg:
 *
 * $("#snippet_keyword").tagit();
 * $("#snippet_keyword").tagit("assignedTags")
 * $("#snippet_keyword").tagit("getTags")
 *
 */
(function ($) {
    var tagit = {
        "addTag": function (tag) {
            var element;
            var self = $(this);

            if (typeof tag === "string") {

                var selection = $(this).find("input[type=hidden]").filter(function () {
                    return $(this).val() == tag;
                });

                // Tag already added
                if (selection.length) {
                    return;
                }

                element = $('<li></li>');
            } else {
                element = $(tag);
                tag = element.text();
            }

            var data = self.data("tagit");

            var hiddenInput = $('<input type="hidden"/>')
                .attr("name", data.field)
                .val(tag);

            element
                .empty()
                .append($("<span></span>").text(tag))
                .append(hiddenInput);

            var close = $('<a class="tagit-close"><span class="text-icon">×</span><span class="ui-icon ui-icon-close"></span></a>');
            close
                .click(function () {
                    $(this).parent().remove();
                });

            element
                .addClass("tagit-choice ui-widget-content ui-state-default ui-corner-all tagit-choice-editable")
                .append(close);

            if (!$(element).parent().length) {
                element.insertBefore($(".tagit-new", self));
            }

            self.trigger("tagit-tag-added", [tag]);
        },

        removeTag: function (tag) {
            var self = $(this);

            var selection = self.find("input[type=hidden]").filter(function () {
                return $(this).val() == tag;
            });

            if (selection.length) {
                selection.parent().remove();
                self.trigger("tagit-tag-removed", [tag]);
            }
        },

        getTags: function () {
            return $.map($(this).find("input[type=hidden]"), function (e) {
                return $.trim($(e).val());
            });
        },

        assignedTags: function () {
            return $.map($(this).find("input[type=hidden]"), function (e) {
                return $.trim($(e).val());
            });
        }
    };

    $.extend($.fn, {
        tagit: function () {
            var args = $.makeArray(arguments);

            var arg0 = args.shift();
            if (tagit[arg0]) {
                return tagit[arg0].apply(this, args);
            }

            return this.each(function () {
                var e = $(this);

                var options = $.extend({}, $.fn.tagit.defaults);
                if ($.isPlainObject(arg0)) {
                    options = $.extend(options, arg0);
                }

                if (e.is(".tagit")) {

                } else {
                    e.data("tagit", options);

                    var input = $('<input type="text" class="no-style" />');
                    var autocomplete = $("<ul></ul>");

                    e.bind("tagit-tag-added", function () {
                        autocomplete.removeClass("open");
                    });

                    e.bind("focusin", function (event) {
                        $(this).addClass("focused");
                    }).bind("focusout", function (event) {
                        $(this).removeClass("focused");
                        input.val("");
                    });

                    input.keydown(function (event) {
                        var self = $(this);
                        var tag = self.val();

                        var keyCode = event.which;

                        // enter key pressed
                        if (keyCode == 13) {
                            if (autocomplete.is(".open")) {
                                var selection = $("li.selected", autocomplete);
                                if (selection.length) {
                                    e.tagit("addTag", selection.text());
                                    self.val("");
                                }
                            }

                            event.preventDefault();
                        } else
                        // tab key pressed
                        if (keyCode == 9) {
                            if (tag) {
                                e.tagit("addTag", self.val());
                                self.val("");

                                event.preventDefault();
                            }
                        } else
                        // up / down arrows pressed
                        if (keyCode == 38 || keyCode == 40) {
                            if (autocomplete.is(".open")) {
                                var elements = $("li", autocomplete);
                                var selection = $(elements).filter(".selected");
                                if (selection.length == 0 && elements.length > 0) {
                                    elements.eq(keyCode == 38 ? elements.length - 1 : 0)
                                        .addClass("selected");
                                } else {
                                    var selector = keyCode == 38 ? "prev" : "next";
                                    var newSelection = selection
                                        [selector]()
                                        .addClass("selected");

                                    if (newSelection.length) {
                                        selection.removeClass("selected");
                                    }
                                }

                                event.preventDefault();
                            }
                        } else
                        // delete key pressed
                        if (keyCode == 8 && !tag) {
                            self.parent().prev().remove();
                            event.preventDefault();
                        } else {
                            tag = (tag + String.fromCharCode(keyCode)).toLowerCase();
                            if (tag) {
                                var tagitBase = $(this).parents(".tagit")
                                var tags = tagitBase.data("tagit").tags;
                                var currentTags = tagitBase.tagit("getTags");

                                if ($.isFunction(tags)) {
                                    tags = tags(tag);
                                }

                                autocomplete.empty();

                                var availableTags = $.grep(tags, function (e) {
                                    return $.inArray(e, currentTags) == -1;
                                });

                                var count = 0;
                                $.each(availableTags, function (i, e) {
                                    if (e.toLowerCase().indexOf(tag) == 0) {
                                        autocomplete.append($("<li></li>").text(e));
                                        count++;
                                    }
                                });

                                if (count > 0) {
                                    autocomplete.addClass("open");
                                } else {
                                    autocomplete.removeClass("open");
                                }
                            }
                        }
                    });

                    autocomplete.click(function (event) {
                        var target = $(event.target);
                        if (target.is("li")) {
                            $(e).tagit("addTag", target.text());
                        }
                    });

                    e.append($('<li class="tagit-new"></li>').append(input).append(autocomplete))
                        .addClass("tagit ui-widget ui-widget-content ui-corner-all");

                    $("li:not(.tagit-new)", e).each(function () {
                        $(e).tagit("addTag", this);
                    });
                }
            });
        }
    });

    $.fn.tagit.defaults = {
        field: "tag",
        tags: []
    };
})(jQuery);