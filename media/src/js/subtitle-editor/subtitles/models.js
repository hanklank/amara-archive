// Amara, universalsubtitles.org
//
// Copyright (C) 2013 Participatory Culture Foundation
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see
// http://www.gnu.org/licenses/agpl-3.0.html.

var angular = angular || null;

(function() {
    /*
     * amara.subtitles.models
     *
     * Define model classes that we use for subtitles
     */

    var module = angular.module('amara.SubtitleEditor.subtitles.models', []);

    // Add function to match by attributes with in the xml namespace
    $.fn.findXmlID = function(value) {
        return this.filter(function() {
            return $(this).attr('xml:id') == value
        });
    };

    function emptyDFXP(languageCode) {
        /* Get a DFXP string for an empty subtitle set */
        return '<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling" xml:lang="' + languageCode + '">\
    <head>\
        <metadata xmlns:ttm="http://www.w3.org/ns/ttml#metadata">\
            <ttm:title/>\
            <ttm:description/>\
            <ttm:copyright/>\
        </metadata>\
        <styling>' + amaraStyle() + '</styling>\
        <layout>' + bottomRegion() + topRegion() + '</layout>\
    </head>\
    <body region="bottom"><div /></body>\
</tt>';
    };

    function amaraStyle() {
        return '<style xml:id="amara-style" tts:color="white" tts:fontFamily="proportionalSansSerif" tts:fontSize="18px" tts:backgroundColor="transparent" tts:textOutline="black 1px 0px" tts:textAlign="center"/>';
    }

    function bottomRegion() {
        return '<region xml:id="bottom" style="amara-style" tts:extent="100% 20%" tts:origin="0 80%" />';
    }

    function topRegion() {
        return '<region xml:id="top" style="amara-style" tts:extent="100% 20%" tts:origin="0 0" />';
    }

    function preprocessDFXP(xml) {
        // Alter XML that we're loading to ensure that it can work with the editor.
        //
        // This means doing things like ensuring that our expected regions are present
        var doc = $($.parseXML(xml));
        var styling = doc.find('styling');
        var layout = doc.find('layout');
        if(styling.find("style").findXmlID('amara-style').length == 0) {
            styling.append($(amaraStyle()));
        }
        if(layout.find("region").findXmlID('bottom').length == 0) {
            layout.append($(bottomRegion()));
        }
        if(layout.find("region").findXmlID('top').length == 0) {
            layout.append($(topRegion()));
        }
        return doc[0];
    }
    function Subtitle(startTime, endTime, markdown, region, startOfParagraph) {
        /* Represents a subtitle in our system
         *
         * Subtitle has the following properties:
         *   - startTime -- start time in seconds
         *   - endTime -- end time in seconds
         *   - markdown -- subtitle content in our markdown-style format
         *   - region -- subtitle display region (top, or undefined for the default/bottom)
         *   - startOfParagraph -- Are we the start of a new paragraph?
         */
        this.startTime = startTime;
        this.endTime = endTime;
        this.markdown = markdown;
        this.region = region;
        this.startOfParagraph = startOfParagraph;
    }

    Subtitle.prototype.duration = function() {
        if(this.isSynced()) {
            return this.endTime - this.startTime;
        } else {
            return -1;
        }
    }

    Subtitle.prototype.hasWarning = function(type, data) {
	if ((type == "lines" || type == undefined) && (this.lineCount() > 2))
	    return true;
	if ((type == "characterRate" || type == undefined) && (this.characterRate() > 21))
	    return true;
	if ((type == "timing" || type == undefined) && ((this.startTime > -1) && (this.endTime > -1) && (this.endTime - this.startTime < 700)))
	    return true;
	if (type == "longline" || type == undefined) {
	    if (type == "longline" && (data == undefined) && ((this.characterCountPerLine().length == 1) && (this.characterCountPerLine()[0] > 42)))
		return true;
	    var from = (data == undefined) ? 0 : data;
	    var to = (data == undefined) ? (this.characterCountPerLine().length) : (data + 1);
	    for (var i = from ; i < to ; i++) {
		if (this.characterCountPerLine()[i] > 42)
		    return true;
	    }
	}
	return false;
    }

    Subtitle.prototype.content = function() {
        /* Get the content of this subtitle as HTML */
        return dfxp.markdownToHTML(this.markdown);
    }

    Subtitle.prototype.isEmpty = function() {
        return this.markdown == '';
    }

    Subtitle.prototype.characterCount = function() {
        var rawContent = dfxp.markdownToPlaintext(this.markdown);
        // Newline characters are not counted
        return (rawContent.length - (rawContent.match(/\n/g) || []).length);
    }

    Subtitle.prototype.characterRate = function() {
        if(this.isSynced()) {
            return (this.characterCount() * 1000 / this.duration()).toFixed(1);
        } else {
            return "0.0";
        }
    }

    Subtitle.prototype.lineCount = function() {
        return this.markdown.split("\n").length;
    }

    Subtitle.prototype.characterCountPerLine = function() {
        var lines = this.markdown.split("\n");
        var counts = [];
        for(var i = 0; i < lines.length; i++) {
            counts.push(dfxp.markdownToPlaintext(lines[i]).length);
        }
        return counts;
        
    }

    Subtitle.prototype.isSynced = function() {
        return this.startTime >= 0 && this.endTime >= 0;
    }

    Subtitle.prototype.isAt = function(time) {
        return this.isSynced() && this.startTime <= time && this.endTime > time;
    }

    Subtitle.prototype.startTimeSeconds = function() {
        if(this.startTime >= 0) {
            return this.startTime / 1000;
        } else {
            return -1;
        }
    }

    Subtitle.prototype.endTimeSeconds = function() {
        if(this.endTime >= 0) {
            return this.endTime / 1000;
        } else {
            return -1;
        }
    }

    function StoredSubtitle(parser, node, id) {
        /* Subtitle stored in a SubtitleList
         *
         * You should never change the proporties on a stored subtitle directly.
         * Instead use the updateSubtitleContent() and updateSubtitleTime()
         * methods of SubtitleList.
         *
         * If you want a subtitle object that you can change the times/content
         * without saving them to the DFXP store, use the draftSubtitle() method
         * to get a DraftSubtitle.
         * */
        var text = $(node).text().trim();
        Subtitle.call(this, parser.startTime(node), parser.endTime(node),
                text, parser.region(node), parser.startOfParagraph(node));
        this.node = node;
        this.id = id;
    }

    StoredSubtitle.prototype = Object.create(Subtitle.prototype);
    StoredSubtitle.prototype.draftSubtitle = function() {
        return new DraftSubtitle(this);
    }
    StoredSubtitle.prototype.isDraft = false;

    function DraftSubtitle(storedSubtitle) {
        /* Subtitle that we are currently changing */
        Subtitle.call(this, storedSubtitle.startTime, storedSubtitle.endTime,
                storedSubtitle.markdown, storedSubtitle.region, storedSubtitle.startOfParagraph);
        this.storedSubtitle = storedSubtitle;
    }

    DraftSubtitle.prototype = Object.create(Subtitle.prototype);
    DraftSubtitle.prototype.isDraft = true;

    /*
     * Manages a list of subtitles.
     *
     * For functions that return subtitle items, each item will have the
     * following properties:
     *   - startTime -- start time in seconds
     *   - endTime -- end time in seconds
     *   - content -- string of html for the subtitle content
     *   - startOfParagraph -- does this subtitle start a new paragraph?
     *   - region -- Region to position the subtitle (top, or undefined for bottom)
     *   - node -- DOM node from the DFXP XML
     *
     */

    module.service('SubtitleList', [function() {

        var SubtitleList = function() {
            this.parser = new AmaraDFXPParser();
            this.idCounter = 0;
            this.subtitles = [];
            this.syncedCount = 0;
            this.changeCallbacks = [];
            this.pendingChanges = [];
        }

        SubtitleList.prototype.contentForMarkdown = function(markdown) {
            return dfxp.markdownToHTML(markdown);
        }

        SubtitleList.prototype.loadEmptySubs = function(languageCode) {
            this.loadXML(emptyDFXP(languageCode));
        }

        SubtitleList.prototype.loadXML = function(subtitlesXML) {
            this.parser.init(subtitlesXML);
            var syncedSubs = [];
            var unsyncedSubs = [];
            // Needed because each() changes the value of this
            var self = this;
            this.parser.getSubtitles().each(function(index, node) {
                var subtitle = self.makeItem(node);
                if(subtitle.isSynced()) {
                    syncedSubs.push(subtitle);
                } else {
                    unsyncedSubs.push(subtitle);
                }
            });
            syncedSubs.sort(function(s1, s2) {
                return s1.startTime - s2.startTime;
            });
            this.syncedCount = syncedSubs.length;
            // Start with synced subs to the list
            this.subtitles = syncedSubs;
            // append all unsynced subs to the list
            this.subtitles.push.apply(this.subtitles, unsyncedSubs);
            this.reloadDone();
        }

        SubtitleList.prototype.addSubtitlesFromBaseLanguage = function(xml) {
            /*
             * Used when we are translating from one language to another.
             * It loads the latest subtitles for xml and inserts blank subtitles
             * with the same timings and paragraphs into our subtitle list.
             */
            var baseLanguageParser = new AmaraDFXPParser();
            baseLanguageParser.init(xml);
            var baseAttributes = [];
            baseLanguageParser.getSubtitles().each(function(index, node) {
                startTime = baseLanguageParser.startTime(node);
                endTime = baseLanguageParser.endTime(node);
                if(startTime >= 0 && endTime >= 0) {
                    baseAttributes.push({
                        'startTime': startTime,
                        'endTime': endTime,
                        'startOfParagraph': baseLanguageParser.startOfParagraph(node),
                        'region': baseLanguageParser.region(node)
                    });
                }
            });
            baseAttributes.sort(function(s1, s2) {
                return s1.startTime - s2.startTime;
            });
            var that = this;
            _.forEach(baseAttributes, function(baseAttribute) {
                var node = that.parser.addSubtitle(null, {
                    begin: baseAttribute.startTime,
                    end: baseAttribute.endTime,
                });
                that.parser.startOfParagraph(node, baseAttribute.startOfParagraph);
                that.parser.region(node, baseAttribute.region);
                that.subtitles.push(that.makeItem(node));
                that.syncedCount++;
            });
            this.reloadDone();
        }

        SubtitleList.prototype.addChangeCallback = function(callback) {
            this.changeCallbacks.push(callback);
        }

        SubtitleList.prototype.removeChangeCallback = function(callback) {
            var pos = this.changeCallbacks.indexOf(callback);
            if(pos >= 0) {
                this.changeCallbacks.splice(pos, 1);
            }
        }

        SubtitleList.prototype.addChange = function(type, subtitle, extraProps) {
            changeObj = { type: type, subtitle: subtitle };
            if(extraProps) {
                for(key in extraProps) {
                    changeObj[key] = extraProps[key];
                }
            }
            this.pendingChanges.push(changeObj);
        }

        SubtitleList.prototype._invokeChangeCallbacks = function() {
            var changes = this.pendingChanges;
            this.pendingChanges = [];
            for(var i=0; i < this.changeCallbacks.length; i++) {
                this.changeCallbacks[i](changes);
            }
        }
        SubtitleList.prototype.changesDone = function(changeDescription) {
            this._invokeChangeCallbacks();
        }

        SubtitleList.prototype.reloadDone = function() {
            this.addChange('reload', null);
            this._invokeChangeCallbacks();
        }


        SubtitleList.prototype.makeItem = function(node) {
            var idKey = (this.idCounter++).toString(16);

            return new StoredSubtitle(this.parser, node, idKey);
        }

        SubtitleList.prototype.length = function() {
            return this.subtitles.length;
        }

        SubtitleList.prototype.needsAnyTranscribed = function() {
            var length = this.length();
            for(var i=0; i < length; i++) {
                if(this.subtitles[i].markdown == '') {
                    return this.subtitles[i];
                }
            }
            return false;
        }

        SubtitleList.prototype.getSubtitleById = function(id) {
            var length = this.length();
            for(var i=0; i < length; i++) {
                if(this.subtitles[i].id == id) {
                    return this.subtitles[i];
                }
            }
            return undefined;
        }

        SubtitleList.prototype.needsAnySynced = function() {
            return this.syncedCount < this.length();
        }

        SubtitleList.prototype.isComplete = function() {
            return (this.length() > 0 &&
                    !this.needsAnyTranscribed() &&
                    !this.needsAnySynced());
        }

        SubtitleList.prototype.firstInvalidTiming = function() {
            var length = this.length();
            for(var i=0; i < length; i++) {
                if((this.subtitles[i].startTime < 0) ||
                   (this.subtitles[i].endTime < 0)) {
                    return this.subtitles[i];
                }
            }
            for(var i=0; i < length; i++) {
                if(this.subtitles[i].startTime >= this.subtitles[i].endTime) {
                    return this.subtitles[i];
                }
            }
            var startTimes = {};
            for(var i=0; i < length; i++) {
                if(startTimes[this.subtitles[i].startTime]) {
                    return this.subtitles[i];
                } else {
                    startTimes[this.subtitles[i].startTime] = true;
                }
            }
            return undefined;
        }

        SubtitleList.prototype.toXMLString = function() {
            return this.parser.xmlToString(true, true);
        }

        SubtitleList.prototype.getIndex = function(subtitle) {
            // Maybe a binary search would be faster, but I think Array.indexOf should
            // be pretty optimized on most browsers.
            return this.subtitles.indexOf(subtitle);
        }

        SubtitleList.prototype.nextSubtitle = function(subtitle) {
            if(subtitle === this.subtitles[this.length() - 1]) {
                return null;
            } else {
                return this.subtitles[this.getIndex(subtitle) + 1];
            }
        }

        SubtitleList.prototype.prevSubtitle = function(subtitle) {
            if(subtitle === this.subtitles[0]) {
                return null;
            } else {
                return this.subtitles[this.getIndex(subtitle) - 1];
            }
        }

        SubtitleList.prototype._updateSubtitle = function(subtitle, attrs) {
            var wasSynced = subtitle.isSynced();

            if(attrs.startTime !== undefined && subtitle.startTime != attrs.startTime) {
                this.parser.startTime(subtitle.node, attrs.startTime);
                subtitle.startTime = attrs.startTime;
            }
            if(attrs.endTime !== undefined && subtitle.endTime != attrs.endTime) {
                this.parser.endTime(subtitle.node, attrs.endTime);
                subtitle.endTime = attrs.endTime;
            }

            if(attrs.content !== undefined) {
                this.parser.content(subtitle.node, attrs.content);
                subtitle.markdown = attrs.content;
            }

            if(attrs.startOfParagraph !== undefined) {
                this.parser.startOfParagraph(subtitle.node, attrs.startOfParagraph);
                subtitle.startOfParagraph = attrs.startOfParagraph;
            }

            if(subtitle.isSynced() && !wasSynced) {
                this.syncedCount++;
            }
            if(!subtitle.isSynced() && wasSynced) {
                this.syncedCount--;
            }
            this.addChange('update', subtitle);
        }

        SubtitleList.prototype._insertSubtitleBefore = function(otherSubtitle, attrs, content) {
            if(otherSubtitle !== null) {
                var pos = this.getIndex(otherSubtitle);
            } else {
                var pos = this.subtitles.length;
            }
            // We insert the subtitle before the reference point, but AmaraDFXPParser
            // wants to insert it after, so we need to adjust things a bit.
            if(pos > 0) {
                var after = this.subtitles[pos-1].node;
            } else {
                var after = -1;
            }
            var node = this.parser.addSubtitle(after, attrs, content);
            var subtitle = this.makeItem(node);
            this.subtitles.splice(pos, 0, subtitle);
            if(subtitle.isSynced()) {
                this.syncedCount++;
            }
            this.addChange('insert', subtitle, { 'before': otherSubtitle});
            return subtitle;
        }

        SubtitleList.prototype._removeSubtitle = function(subtitle) {
            var pos = this.getIndex(subtitle);
            this.parser.removeSubtitle(subtitle.node);
            this.subtitles.splice(pos, 1);
            if(subtitle.isSynced()) {
                this.syncedCount--;
            }
            this.addChange('remove', subtitle);
        }


        SubtitleList.prototype.updateSubtitleTime = function(subtitle, startTime, endTime) {
            this._updateSubtitle(subtitle, {startTime: startTime, endTime: endTime});
            this.changesDone('Time change');
        }

        SubtitleList.prototype.updateSubtitleContent = function(subtitle, content) {
            this._updateSubtitle(subtitle, {content: content});
            this.changesDone('Subtitle edit');
        }

        SubtitleList.prototype.updateSubtitleParagraph = function(subtitle, startOfParagraph) {
            // If startOfParagraph is not given, it is toggled
            if(startOfParagraph === undefined) {
                startOfParagraph = !subtitle.startOfParagraph;
            }
            this._updateSubtitle(subtitle, {startOfParagraph: startOfParagraph});
            this.changesDone('Paragraph change');
        }

        SubtitleList.prototype.getSubtitleParagraph = function(subtitle) {
            return this.parser.startOfParagraph(subtitle.node);
        }

        SubtitleList.prototype._setRegion = function(subtitle, region) {
            subtitle.region = region;
            this.parser.region(subtitle.node, region);
            this.addChange('update', subtitle);
        }

        SubtitleList.prototype.setRegion = function(subtitle, region) {
            this._setRegion(subtitle, region);
            this.changesDone('Position change');
        }

        SubtitleList.prototype.insertSubtitleBefore = function(otherSubtitle, region) {
            var attrs = {
                region: region
            }
            var defaultDuration = 3000;

            if(otherSubtitle && otherSubtitle.isSynced()) {
                // If we are inserting between 2 synced subtitles, then we can set the
                // time
                var previousSubtitle = this.prevSubtitle(otherSubtitle);
                if(previousSubtitle) {
                    // Inserting a subtitle between two others.
                    var gapDuration = otherSubtitle.startTime - previousSubtitle.endTime;
                    if(gapDuration > defaultDuration) {
                        // The gap between the previousSubtitle and otherSubtitle is long enough to fit the new subtitle inside.  Put the subtitle in the middle of that gap
                        attrs.begin = previousSubtitle.endTime + ((gapDuration - defaultDuration) / 2);
                        attrs.end = attrs.begin + defaultDuration;
                    } else {
                        // The gap is not enough to fit new subtitle inside, move the previousSubtitle.endTime back to fit it.
                        // But... don't move it so far back that previousSubtitle is now shorter than the new subtitle
                        attrs.begin = Math.max(otherSubtitle.startTime - defaultDuration, (previousSubtitle.startTime + otherSubtitle.startTime) / 2);
                        this._updateSubtitle(previousSubtitle, {endTime: attrs.begin});
                        attrs.end = otherSubtitle.startTime;
                    }
                } else {
                    // Inserting a subtitle as the start of the list.
                    if(otherSubtitle.startTime >= defaultDuration) {
                        // The gap is large enough for the new subtitle, put it in the middle
                        attrs.begin = (otherSubtitle.startTime - defaultDuration) / 2;
                        attrs.end = attrs.begin + defaultDuration;
                    } else {
                        // The gap is not large enough for the new subtitle to fit inside, move otherSubtitle.startTime forward to fit it in
                        // But don't move it so far forward that otherSubtitle is now shorter than the new subtitle
                        attrs.begin = 0;
                        attrs.end = Math.min(defaultDuration, otherSubtitle.endTime / 2);
                        this._updateSubtitle(otherSubtitle, {startTime: attrs.end});
                    }
                }
            }
            var subtitle = this._insertSubtitleBefore(otherSubtitle, attrs);
            this.changesDone('Insert subtitle');
            return subtitle;
        }

        // Take a subtitle and split it in half.
        //
        // subtitle will now take up only the first half of the time and get firstSubtitleMarkdown as its content
        // A new subtitle will be created to take up the second half of the time and get secondSubtitleMarkdown as its content
        SubtitleList.prototype.splitSubtitle = function(subtitle, firstSubtitleMarkdown, secondSubtitleMarkdown) {
            if(subtitle.isSynced()) {
                var midpointTime = (subtitle.startTime + subtitle.endTime) / 2;
                var newSubAttrs = {
                    begin: midpointTime,
                    end: subtitle.endTime,
                    region: subtitle.region
                }

                this._updateSubtitle(subtitle, {
                    endTime: midpointTime,
                    content: firstSubtitleMarkdown
                });
            } else {
                var newSubAttrs = { region: subtitle.region }

                this._updateSubtitle(subtitle, {content: firstSubtitleMarkdown});
            }
            var newSubtitle = this._insertSubtitleBefore(this.nextSubtitle(subtitle), newSubAttrs, secondSubtitleMarkdown);
            this.changesDone('Split subtitle');

            return newSubtitle;
        }

        SubtitleList.prototype.removeSubtitle = function(subtitle) {
            this._removeSubtitle(subtitle);
            this.changesDone();
        }

        SubtitleList.prototype.lastSyncedSubtitle = function() {
            if(this.syncedCount > 0) {
                return this.subtitles[this.syncedCount - 1];
            } else {
                return null;
            }
        }

        SubtitleList.prototype.firstUnsyncedSubtitle = function() {
            if(this.syncedCount < this.subtitles.length) {
                return this.subtitles[this.syncedCount];
            } else {
                return null;
            }
        }

        SubtitleList.prototype.secondUnsyncedSubtitle = function() {
            if(this.syncedCount + 1 < this.subtitles.length) {
                return this.subtitles[this.syncedCount + 1];
            } else {
                return null;
            }
        }

        SubtitleList.prototype.indexOfFirstSubtitleAfter = function(time) {
            /* Get the first subtitle whose end is after time
             *
             * returns index of the subtitle, or -1 if none are found.
             */

            // Do a binary search to find the sub
            var left = 0;
            var right = this.syncedCount-1;
            // First check that we are going to find any subtitle
            if(right < 0 || this.subtitles[right].endTime <= time) {
                return -1;
            }
            // Now do the binary search
            while(left < right) {
                var index = Math.floor((left + right) / 2);
                if(this.subtitles[index].endTime > time) {
                    right = index;
                } else {
                    left = index + 1;
                }
            }
            return left;
        }

        SubtitleList.prototype.firstSubtitle = function() {
            return this.subtitles[this.indexOfFirstSubtitleAfter(-1)] ||
                   this.firstUnsyncedSubtitle();
        }

        SubtitleList.prototype.lastSubtitle = function() {
            return this.subtitles[this.subtitles.length -1];
        }

        SubtitleList.prototype.subtitleAt = function(time) {
            /* Find the subtitle that occupies a given time.
             *
             * returns a StoredSubtitle, or null if no subtitle occupies the time.
             */
            var i = this.indexOfFirstSubtitleAfter(time);
            if(i == -1) {
                return null;
            }
            var subtitle = this.subtitles[i];
            if(subtitle.isAt(time)) {
                return subtitle;
            } else {
                return null;
            }
        }

        SubtitleList.prototype.getSubtitlesForTime = function(startTime, endTime) {
            var rv = [];
            var i = this.indexOfFirstSubtitleAfter(startTime);
            if(i == -1) {
                return rv;
            }
            for(; i < this.syncedCount; i++) {
                var subtitle = this.subtitles[i];
                if(subtitle.startTime < endTime) {
                    rv.push(subtitle);
                } else {
                    break;
                }
            }
            return rv;
        }

        return SubtitleList;
    }]);

    /*
     * CurrentEditManager manages the current in-progress edit
     */
    module.service('CurrentEditManager', [function() {
        CurrentEditManager = function() {
            this.draft = null;
            this.LI = null;
        }

        CurrentEditManager.prototype = {
            start: function(subtitle, LI) {
                this.draft = subtitle.draftSubtitle();
                this.LI = LI;
            },
            finish: function(commitChanges, subtitleList) {
                var updateNeeded = (commitChanges && this.changed());
                if(updateNeeded) {
                    subtitleList.updateSubtitleContent(this.draft.storedSubtitle,
                            this.currentMarkdown());
                }
                this.draft = this.LI = null;
                return updateNeeded;
            },
            storedSubtitle: function() {
                if(this.draft !== null) {
                    return this.draft.storedSubtitle;
                } else {
                    return null;
                }
            },
            sourceMarkdown: function() {
                return this.draft.storedSubtitle.markdown;
            },
            currentMarkdown: function() {
                return this.draft.markdown;
            },
            changed: function() {
                return this.sourceMarkdown() != this.currentMarkdown();
            },
             update: function(markdown) {
                if(this.draft !== null) {
                    this.draft.markdown = markdown;
                }
             },
             isForSubtitle: function(subtitle) {
                return (this.draft !== null && this.draft.storedSubtitle == subtitle);
             },
             inProgress: function() {
                return this.draft !== null;
             },
             lineCounts: function() {
                 if(this.draft === null || this.draft.lineCount() < 2) {
                     // Only show the line counts if there are 2 or more lines
                     return null;
                 } else {
                     return this.draft.characterCountPerLine();
                 }
             },
        };

        return CurrentEditManager;
    }]);

    /*
     * SubtitleVersionManager: handle the active subtitle version for the
     * reference and working subs.
     *
     */

    module.service('SubtitleVersionManager', ['SubtitleList', function(SubtitleList) {
        SubtitleVersionManager = function(video, SubtitleStorage) {
            this.video = video;
            this.SubtitleStorage = SubtitleStorage;
            this.subtitleList = new SubtitleList();
            this.versionNumber = null;
            this.language = null;
            this.title = null;
            this.description = null;
            this.state = 'waiting';
            this.metadata = {};
        }

        SubtitleVersionManager.prototype = {
            getSubtitles: function(languageCode, versionNumber) {
                this.setLanguage(languageCode);
                this.versionNumber = versionNumber;
                this.state = 'loading';

                var that = this;

                this.SubtitleStorage.getSubtitles(languageCode, versionNumber,
                        function(subtitleData) {
                    that.state = 'loaded';
                    that.title = subtitleData.title;
                    that.initMetadataFromVideo();
                    for(key in subtitleData.metadata) {
                        that.metadata[key] = subtitleData.metadata[key];
                    }
                    that.description = subtitleData.description;
                    var subtitles = preprocessDFXP(subtitleData.subtitles);
                    that.subtitleList.loadXML(subtitles);
                });
            },
            initEmptySubtitles: function(languageCode, baseLanguage) {
                this.setLanguage(languageCode);
                this.versionNumber = null;
                this.title = '';
                this.description = '';
                this.subtitleList.loadEmptySubs(languageCode);
                this.state = 'loaded';
                this.initMetadataFromVideo();
                if(baseLanguage) {
                    this.addSubtitlesFromBaseLanguage(baseLanguage);
                }
            },
            initMetadataFromVideo: function() {
                this.metadata = {};
                for(key in this.video.metadata) {
                    this.metadata[key] = '';
                }
            },
            addSubtitlesFromBaseLanguage: function(baseLanguage) {
                var that = this;
                this.SubtitleStorage.getSubtitles(baseLanguage, null,
                        function(subtitleData) {
                    that.subtitleList.addSubtitlesFromBaseLanguage(
                        subtitleData.subtitles);
                });
            },
            setLanguage: function(code) {
                this.language = this.SubtitleStorage.getLanguage(code);
            },
            getTitle: function() {
                if(!this.language) {
                    return '';
                } else if(this.language.isPrimaryAudioLanguage) {
                    return this.title || this.video.title;
                } else {
                    return this.title;
                }
            },
            getDescription: function() {
                if(!this.language) {
                    return '';
                } else if(this.language.isPrimaryAudioLanguage) {
                    return this.description || this.video.description;
                } else {
                    return this.description;
                }
            },
            getMetadata: function() {
                var metadata = _.clone(this.metadata);
                if(this.language.isPrimaryAudioLanguage) {
                    for(key in metadata) {
                        if(!metadata[key]) {
                            metadata[key] = this.video.metadata[key];
                        }
                    }
                }
                return metadata;
            }
        };

        return SubtitleVersionManager;
    }]);

}(this));
