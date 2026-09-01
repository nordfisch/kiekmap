# Guide for the museum team

> Meant to be printed and left beside the device — screenshots follow once the device stands in
> the museum.

## Getting into the admin area

The **coat of arms** sits at the top left of the map. Tap it once, enter the **PIN** and tap
"Continue".

Whoever does not know the PIN does not get in — that is deliberate. After five wrong entries the
device waits a minute before it takes the next one.

You can go back to the map at any time with **"Leave the admin area"** at the top right. If you
forget, the device signs itself out after half an hour.

## Adding photos

Admin area → **Import**. The page asks two things, in this order:

**Choosing the pictures to import**

Two tiles stand at the top; the chosen one has a border. Below them is always the same area, only
its content changes:

- **From the computer** — tap **"Choose"** and click the files. With a mouse you can drag them
  onto the area instead.
- **From a USB stick** — plug the stick in. The folders with pictures appear in the area by
  themselves; choose one of them. *Nothing on the stick is changed, only read.*

**Details for all newly added pictures (optional)**

*Year* and *Place* for the whole batch — with forty pictures of the same parish fair that saves
thirty-nine entries. Both can be changed per picture afterwards.

**"Precision"** stands beside the year: *Year* or *Decade*. As long as no year is entered, nothing
can be chosen there. *Decade* exists only for round numbers such as 1920 or 1930 — with 1923 it
would not be clear what is meant. Whoever picks 1920 and Decade and then changes the number to
1923 gets *Year* back automatically.

Then **"Import"**. The device shows which picture it is at.

> **There is a third way, entirely without the admin area:** copy the pictures into the folder
> `incoming` on the computer. The device takes them in by itself and afterwards moves the files
> into the subfolder `_done`. Nothing is deleted there either.

### After the import

With a manageable number of pictures a list appears: the picture on the left, title, year and
place beside it. The **title is suggested from the file name** — `Kirchweih_1932_Muehle.jpg`
becomes "Kirchweih 1932 Muehle".

With very many pictures at once it only says how many there are, and a button into the list
**"Without a place"**. A table of two hundred rows would be no place to work.

Change what you know and tap **"Apply"**. The row then disappears. **"Apply all"** deals with the
rest in one go.

> **The pictures are saved already, before you apply anything.** You can leave the list at any
> time without losing something. What you leave lying turns up later by itself in the "Help out"
> panel and gets answered there by visitors.

If a picture was there before, the device says so ("3 were already there"). No second copy comes
into being.

## Filling in and correcting records

Admin area → **Photos**. With **"Without a place"** and **"Without a year"** you see exactly the
pictures where the one or the other is missing — those are the lists to work through. The search
field finds a particular picture by title, place or file name.

**The shortest way there is the start page:** every number of the overview leads straight into the
matching list. Tap "4 without a year" and you are there.

With more than thirty pictures, **"Back · Page 1 of 3 · Next"** stands below the list. After
editing a picture you are on the same page again. Change the filter or search for something and it
starts at page 1 again.

"Edit" opens the form. For the **place** there is a search by street name; it works without the
internet.

Two particulars:

- An **empty year field means "unknown"**. If you delete a wrong year and save, the picture counts
  as undated again — and is put to visitors once more. That is intended.
- A picture can be **hidden** instead of deleted. It then disappears from the map but is kept and
  stays findable in the admin area. The device cannot delete.

## What visitors have contributed

Admin area → **Moderation**. What visitors have entered on the screen stands here.

If something is obviously wrong, tap **"Take back"**. The record is deleted and the picture goes
back into the "Help out" panel — perhaps the next visitor knows better.

If **"Edited by hand"** stands there instead of a button, somebody from the team has reworked the
record since. Taking it back would throw that work away with it, so it is no longer possible.

> **Which decades visitors are offered** follows from the collection itself: everything that
> occurs in it, but at least the 1920s to the 2010s. If a button for a very old photo is missing,
> date a single picture from that time under **Photos → Edit** — the decade is then available to
> visitors as well.

## When something does not arrive

Admin area → **Log**. Every file the device has looked at stands there, with the reason: taken in,
duplicate or rejected. There is no "nothing happened" here — if a picture is missing, the reason
stands here.

## Backup onto a USB stick

Once a year, and always after a larger batch of new pictures. The start page of the admin area
says at the bottom left how many days have passed since the last backup; if it is longer than a
month ago, the tile turns red. Tapping it leads straight here.

1. **Plug the USB stick in.** An ordinary stick will do. It should have as much room as the
   collection is large — the device works it out for you.
2. Admin area → **Backup**. The stick appears by itself as soon as it is in.
3. Once its name and "enough for … photos" stand there, tap **"Start the backup"**.
4. Wait. The device shows which picture it is at. **Do not pull the stick out while the bar is
   running.**
5. At the end it says "… photos and all records saved. The stick can be removed now." Only then
   pull it out.

**The second time is quick.** The device writes only what has come in since the last time. If it
says "There were no new pictures" at the end, that is not an error but means: everything was on
the stick already.

You can use the same stick over and over. A folder `kiekmap-backup` lies on it — you can open that
on any computer, the pictures lie there as ordinary files.

> **If no stick appears:** is it in properly? Some very old sticks are not recognised. Another
> stick is the quickest thing to try.

> **If you give a backup out of the house** — to another museum, to a company, to somebody to try
> out: besides your photos the database also holds the place index, and that comes from
> OpenStreetMap. Please add the note "Place data: © OpenStreetMap contributors, ODbL" to it. One
> sentence in the email will do. Nothing changes for your own photos — they still belong to the
> museum.

## Downloading the backup as one file

If no stick is to hand, it also works through the computer you are sitting at: Admin area →
**Backup** → tile **"As one file"** → **"Download the backup"**. You get the whole collection as
one ZIP file.

**The stick stays the better way**, for two reasons: onto the stick the device writes only what is
new the second time — the file holds everything every time and takes correspondingly long. And if
the download breaks off, the file is unusable, while a backup broken off on the stick is not.

So the file is the addition, not the replacement. For the backup that stays in the museum, take
the stick.

> **How does such a file get back into the device?** In two ways. On the computer: put the ZIP
> file into the folder `incoming`. The device recognises it by itself and asks in the backup area
> whether it should be read in — **nothing happens on its own.** Or by stick: unpack the file so
> that the folder `kiekmap-backup` lies there, plug the stick in, and then go by the next section.

## Reading a backup back in

You only need this when the device was set up again or something really has been lost. **The
collection as it stands is replaced.**

1. Plug the stick in, Admin area → **Backup**.
2. Right at the bottom **"Restore"**.
3. The device asks back and names the date and the count of the backup. Only then does it start.

What was on the device before is **not deleted** but set aside into a folder with today's date.
So whoever reads the wrong backup in by mistake has lost nothing — tell somebody in that case who
can get at the device.

### When the backup is older than the program

That is the normal case, and **you need do nothing for it**. A backup holds the records in the
form the program had at the time; if the program has been renewed since, it brings the records it
reads back in to its present form itself. "The schema is being brought forward" then stands
briefly on the progress bar.

*Until August 2026 you had to restart the device by hand afterwards. Without the restart the
exhibition looked right but took nothing in any more. That is fixed.*

### When the backup is newer than the program

The other way round — a backup from a freshly updated device on one that has not been updated yet.
Then **reading it back in breaks off** and tells you so:

> This backup belongs to a newer version of the program. Please update the program first, then
> read the backup in. Nothing on the device was changed.

**The collection on the device stays untouched** — nothing is half replaced. Tell somebody who can
update the program; the same backup can be read in afterwards.

## What to do when the screen stays black

First: is the plug in, is the screen on? If so, a restart usually helps — switch the device off,
wait ten seconds, switch it on again. After about twenty seconds the map should appear by itself.

**If the display only sticks without the screen being black**, there is a gentler way: Admin area
→ **"Reload the display"** right at the bottom of the start page. It takes a moment and changes
nothing in the collection. The same happens by itself as soon as the device is untouched for five
minutes — so overnight it stands fresh again by morning anyway.

If it stays that way, only somebody with access to the device can help further. What they need to
know is in [operations.md](operations.md).
