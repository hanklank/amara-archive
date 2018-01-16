
/*
 * Amara, universalsubtitles.org
 *
 * Copyright (C) 2018 Participatory Culture Foundation
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see
 * http://www.gnu.org/licenses/agpl-3.0.html.
 */


var angular = angular || null;

(function() {
    var module = angular.module('amara.SubtitleEditor.shifttime', []);

    module.controller("ShiftForwardController", ['$scope', function($scope) {
        $scope.shiftAmountError = false;
        $scope.startFromError = false;
        $scope.shiftForward = function($event) {
        };
        $scope.shiftBackward = function($event) {
        };

        $scope.doShift = function(from, amount) {
            var nextWorkingSubtitle = $scope.workingSubtitles.subtitleList.firstSubtitle();
            while (nextWorkingSubtitle) {
                if (nextWorkingSubtitle.startTime >= from) {
                    $scope.workingSubtitles.subtitleList.updateSubtitleTime(nextWorkingSubtitle,
                                                                        nextWorkingSubtitle.startTime + amount,
                                                                        nextWorkingSubtitle.endTime + amount);
                }
                nextWorkingSubtitle = $scope.workingSubtitles.subtitleList.nextSubtitle(nextWorkingSubtitle);
            }
            $scope.$root.$emit('work-done');
        };
        $scope.doShiftForward = function($event) {
            $scope.shiftAmountError = false;
            $scope.startFromError = false;
            var subsToShift = $("#forward input[name=subs-to-shift]:checked").val();
            var from = 0;
            if (subsToShift == "after") {
                var startFrom = $("#forward input[name=start-from]").val();
                var re = /(\d+)\:(\d+)\:(\d+)\.(\d{1,3})/;
                var parsed = re.exec(startFrom);
                if (parsed) {
                    from = parseInt(parsed[4].padEnd(3,"0")) + 1000 * (parseInt(parsed[3]) + 60 * (parseInt(parsed[2]) + 60 * parseInt(parsed[1])));
                } else {
                    $scope.startFromError = true;
                    return;
                }
            }
            var shiftAmount = parseInt($("#forward input[name=mseconds]").val() || "0") + 1000 * (parseInt($("#forward input[name=seconds]").val() || 0) + 60 * (parseInt($("#forward input[name=minutes]").val() || 0) + 60 * parseInt($("#forward input[name=hours]").val() || 0)));
            if (isNaN(shiftAmount)) {
                $scope.shiftAmountError = true;
                return;
            } else {
                $scope.doShift(from, shiftAmount);
            }
        };
        $scope.doShiftBackward = function($event) {
            $scope.shiftAmountError = false;
            $scope.startFromError = false;
            var subsToShift = $("#backward input[name=subs-to-shift]:checked").val();
            var from = 0;
            if (subsToShift == "after") {
                var startFrom = $("#backward input[name=start-from]").val();
                var re = /(\d+)\:(\d+)\:(\d+)\.(\d{1,3})/;
                var parsed = re.exec(startFrom);
                if (parsed) {
                    from = parseInt(parsed[4].padEnd(3,"0")) + 1000 * (parseInt(parsed[3]) + 60 * (parseInt(parsed[2]) + 60 * parseInt(parsed[1])));
                } else {
                    $scope.startFromError = true;
                    return;
                }
            }
            var shiftAmount = parseInt($("#backward input[name=mseconds]").val() || "0") + 1000 * (parseInt($("#backward input[name=seconds]").val() || 0) + 60 * (parseInt($("#backward input[name=minutes]").val() || 0) + 60 * parseInt($("#backward input[name=hours]").val() || 0)));
            if (isNaN(shiftAmount)) {
                $scope.shiftAmountError = true;
                return;
            } else {
                $scope.doShift(from, -shiftAmount);
            }
        };
        $scope.dataValid = function() {
            return false;
        }
    }]);
    module.controller("ShiftBackwardController", ['$scope', function($scope) {
        $scope.dataValid = function() {
            return false;
        }
    }]);
}).call(this);
