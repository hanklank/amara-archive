describe('Test the SubtitleList class', function() {
    var subtitleList = null;

    beforeEach(module('amara.SubtitleEditor.subtitles.models'));
    beforeEach(module('amara.SubtitleEditor.mocks'));

    beforeEach(inject(function(SubtitleList) {
        subtitleList = new SubtitleList();
        subtitleList.loadEmptySubs('en');

        jasmine.addMatchers({
            toHaveTimes: function(util, customEqualityTesters) {
                return {
                    compare: function(actual, expected) {
                        var result = {};
                        result.pass = util.equals([actual.startTime, actual.endTime], expected);
                        return result;
                    }
                };
            }
        });
    }));

    it('should start empty', function() {
        expect(subtitleList.subtitles).toEqual([]);
    });

    it('should support insertion and removal', function() {
        var sub1 = subtitleList.insertSubtitleBefore(null);
        var sub2 = subtitleList.insertSubtitleBefore(sub1);
        var sub3 = subtitleList.insertSubtitleBefore(null);
        expect(subtitleList.subtitles).toEqual([sub2, sub1, sub3]);
        subtitleList.removeSubtitle(sub1);
        expect(subtitleList.subtitles).toEqual([sub2, sub3]);
        subtitleList.removeSubtitle(sub2);
        expect(subtitleList.subtitles).toEqual([sub3]);
        subtitleList.removeSubtitle(sub3);
        expect(subtitleList.subtitles).toEqual([]);
    });

    it('supports regions when inserting', function() {
        var sub = subtitleList.insertSubtitleBefore(null, "top");
        expect(sub.region).toEqual('top');
    });

    it('should update content', function() {
        var sub1 = subtitleList.insertSubtitleBefore(null);
        expect(sub1.content()).toEqual('');
        subtitleList.updateSubtitleContent(sub1, 'test');
        expect(sub1.content()).toEqual('test');
        subtitleList.updateSubtitleContent(sub1, '*test*');
        expect(sub1.content()).toEqual('<i>test</i>');
        subtitleList.updateSubtitleContent(sub1, '**test**');
        expect(sub1.content()).toEqual('<b>test</b>');
    });

    it('should update timing', function() {
        var sub1 = subtitleList.insertSubtitleBefore(null);
        var sub2 = subtitleList.insertSubtitleBefore(null);
        expect(subtitleList.syncedCount).toEqual(0);
        subtitleList.updateSubtitleTime(sub1, 500, 1500);
        expect(sub1).toHaveTimes([500, 1500]);
        expect(subtitleList.syncedCount).toEqual(1);
        subtitleList.updateSubtitleTime(sub1, 1000, 1500);
        expect(sub1).toHaveTimes([1000, 1500]);
        expect(subtitleList.syncedCount).toEqual(1);
        subtitleList.updateSubtitleTime(sub2, 2000, 2500);
        expect(sub2).toHaveTimes([2000, 2500]);
        expect(subtitleList.syncedCount).toEqual(2);
    });

    it('should get and update regions', function() {
        var sub = subtitleList.insertSubtitleBefore(null);
        expect(sub.region).toEqual(undefined);
        subtitleList.setRegion(sub, 'top');
        expect($(sub.node).attr('region')).toEqual('top');
        expect(sub.region).toEqual('top');
    });

    it('should invoke change callbacks', function() {
        var handler = jasmine.createSpyObj('handler', ['onChange']);
        subtitleList.addChangeCallback(handler.onChange);

        var sub = subtitleList.insertSubtitleBefore(null);
        expect(handler.onChange.calls.count()).toEqual(1);
        expect(handler.onChange).toHaveBeenCalledWith([{
            type: 'insert',
            subtitle: sub,
            before: null,
        }]);

        subtitleList.updateSubtitleTime(sub, 500, 1500);
        expect(handler.onChange.calls.count()).toEqual(2);
        expect(handler.onChange).toHaveBeenCalledWith([{
            type: 'update',
            subtitle: sub,
        }]);

        subtitleList.updateSubtitleContent(sub, 'content');
        expect(handler.onChange.calls.count()).toEqual(3);
        expect(handler.onChange).toHaveBeenCalledWith([{
            type: 'update',
            subtitle: sub,
        }]);

        subtitleList.removeSubtitle(sub);
        expect(handler.onChange.calls.count()).toEqual(4);
        expect(handler.onChange).toHaveBeenCalledWith([{
            type: 'remove',
            subtitle: sub,
        }]);

        subtitleList.removeChangeCallback(handler.onChange);
        var sub2 = subtitleList.insertSubtitleBefore(null);
        subtitleList.updateSubtitleTime(sub2, 500, 1500);
        subtitleList.updateSubtitleContent(sub2, 'content');
        subtitleList.removeSubtitle(sub2);
        expect(handler.onChange.calls.count()).toEqual(4);
    });

    describe('insertBefore unsynced subtitle', function() {
        it('appends at the end if otherSubtitle is null', function() {
            var sub1 = subtitleList.insertSubtitleBefore(null);
            var sub2 = subtitleList.insertSubtitleBefore(null);
            expect(subtitleList.subtitles).toEqual([sub1, sub2]);
        });

        it('inserts unsynced subtitles otherSubtitle is unsynced', function() {
            var sub1 = subtitleList.insertSubtitleBefore(null);
            var sub2 = subtitleList.insertSubtitleBefore(sub1);
            expect(subtitleList.subtitles).toEqual([sub2, sub1]);
            expect(sub2.startTime).toEqual(-1);
            expect(sub2.endTime).toEqual(-1);
        });
    });

    describe('insertBefore with two synced subtitles', function() {
        var sub1, sub2;
        beforeEach(function() {
            sub1 = subtitleList.insertSubtitleBefore(null);
            sub2 = subtitleList.insertSubtitleBefore(null);
        });
        it('inserts a 3 second subtitle in the between otherSubtitle and the previous subtitle, if there is a 3 second gap', function() {
            subtitleList.updateSubtitleTime(sub1, 0, 1000);
            subtitleList.updateSubtitleTime(sub2, 5000, 6000);
            var newSub = subtitleList.insertSubtitleBefore(sub2);

            expect(subtitleList.subtitles).toEqual([sub1, newSub, sub2]);
            expect(newSub).toHaveTimes([1500, 4500]);
        });

        it('adjusts the end time of the previous subtitle to make room for the new subtitle, if there is less than a 3 second gap', function() {
            subtitleList.updateSubtitleTime(sub1, 0, 4000);
            subtitleList.updateSubtitleTime(sub2, 6000, 7000);
            var newSub = subtitleList.insertSubtitleBefore(sub2);

            expect(subtitleList.subtitles).toEqual([sub1, newSub, sub2]);
            expect(sub1).toHaveTimes([0, 3000]);
            expect(newSub).toHaveTimes([3000, 6000]);
        });

        it('splits the time between the previous subtitle and the new subtitle if there is less than 6 seconds for them both', function() {
            subtitleList.updateSubtitleTime(sub1, 0, 2000);
            subtitleList.updateSubtitleTime(sub2, 3000, 7000);
            var newSub = subtitleList.insertSubtitleBefore(sub2);

            expect(subtitleList.subtitles).toEqual([sub1, newSub, sub2]);
            expect(sub1).toHaveTimes([0, 1500]);
            expect(newSub).toHaveTimes([1500, 3000]);
        });
    });

    describe('insertBefore with first synced subtitle', function() {
        var sub1;
        beforeEach(function() {
            sub1 = subtitleList.insertSubtitleBefore(null);
        });

        it('inserts a 3 second subtitle in the middle of the initial empty time, if there is a 3 second gap', function() {
            subtitleList.updateSubtitleTime(sub1, 4000, 5000);
            var newSub = subtitleList.insertSubtitleBefore(sub1);

            expect(subtitleList.subtitles).toEqual([newSub, sub1]);
            expect(newSub).toHaveTimes([500, 3500]);
        });

        it('adjusts the start time of the next subtitle to make room for the new subtitle, if there is less than a 3 second gap', function() {
            subtitleList.updateSubtitleTime(sub1, 2000, 7000);
            var newSub = subtitleList.insertSubtitleBefore(sub1);

            expect(subtitleList.subtitles).toEqual([newSub, sub1]);
            expect(newSub).toHaveTimes([0, 3000]);
            expect(sub1).toHaveTimes([3000, 7000]);
        });

        it('splits the time between the next subtitle and the new subtitle if there is less than 6 seconds for them both', function() {
            subtitleList.updateSubtitleTime(sub1, 2000, 3000);
            var newSub = subtitleList.insertSubtitleBefore(sub1);

            expect(subtitleList.subtitles).toEqual([newSub, sub1]);
            expect(newSub).toHaveTimes([0, 1500]);
            expect(sub1).toHaveTimes([1500, 3000]);
        });
    });

    describe('split subtitles', function() {
        it('splits subtitles', function() {
            var sub1 = subtitleList.insertSubtitleBefore(null);
            subtitleList.updateSubtitleTime(sub1, 0, 8000);

            var sub2 = subtitleList.splitSubtitle(sub1, 'foo', 'bar');

            expect(sub1).toHaveTimes([0, 4000]);
            expect(sub1.markdown).toEqual('foo');
            expect(sub2).toHaveTimes([4000, 8000]);
            expect(sub2.markdown).toEqual('bar');
            expect(subtitleList.syncedCount).toEqual(2);
            expect(subtitleList.firstSubtitle()).toBe(sub1);
            expect(subtitleList.nextSubtitle(sub1)).toBe(sub2);
            expect(subtitleList.nextSubtitle(sub2)).toBe(null);

            var sub3 = subtitleList.splitSubtitle(sub2, 'b', 'ar');

            expect(sub2).toHaveTimes([4000, 6000]);
            expect(sub2.markdown).toEqual('b');
            expect(sub3).toHaveTimes([6000, 8000]);
            expect(sub3.markdown).toEqual('ar');
            expect(subtitleList.syncedCount).toEqual(3);
            expect(subtitleList.firstSubtitle()).toBe(sub1);
            expect(subtitleList.nextSubtitle(sub1)).toBe(sub2);
            expect(subtitleList.nextSubtitle(sub2)).toBe(sub3);
            expect(subtitleList.nextSubtitle(sub3)).toBe(null);
        });

        it('splits unsynced subtitles', function() {
            var sub = subtitleList.insertSubtitleBefore(null);
            var sub2 = subtitleList.splitSubtitle(sub, 'one', 'two');

            expect(sub).toHaveTimes([-1, -1]);
            expect(sub2).toHaveTimes([-1, -1]);
            expect(subtitleList.syncedCount).toEqual(0);
        });

        it('preserves region when splitting subtitles', function() {
            var sub1 = subtitleList.insertSubtitleBefore(null);
            subtitleList.updateSubtitleTime(sub1, 0, 8000);
            subtitleList.setRegion(sub1, 'top');

            var sub2 = subtitleList.splitSubtitle(sub1, 'foo', 'bar');
            expect(sub2.region).toBe('top');
        });

        it('invokes change callbacks on split subtitles', function() {

            var sub1 = subtitleList.insertSubtitleBefore(null);
            subtitleList.updateSubtitleTime(sub1, 0, 8000);

            var handler = jasmine.createSpyObj('handler', ['onChange']);
            subtitleList.addChangeCallback(handler.onChange);

            var sub2 = subtitleList.splitSubtitle(sub1, 'foo', 'bar');
            expect(handler.onChange).toHaveBeenCalledWith([{
                type: 'update',
                subtitle: sub1,
            }, {
                type: 'insert',
                subtitle: sub2,
                before: null,
            }]);

            handler.onChange.calls.reset();
            var sub3 = subtitleList.splitSubtitle(sub1, 'f', 'oo');

            expect(handler.onChange).toHaveBeenCalledWith([{
                type: 'update',
                subtitle: sub1,
            }, {
                type: 'insert',
                subtitle: sub3,
                before: sub2,
            }]);

        });
    });
});

