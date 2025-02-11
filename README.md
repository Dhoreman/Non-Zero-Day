# NON-ZERO-DAYS
#### Video Demo: https://www.youtube.com/watch?v=axlH1JTuTrA
#### Description:

This project was made to help people stay motivated to work on their goals.

We've all been there, we have all these things we want to do on a given day but
for whatever reason we don't and end up laying in bed at night feeling guilty about it.
When this happens a lot, it can cause us stress and anxiety.

If you recognize the problem explained above Non-Zero-Days might be of help to you!


**What's a Non-Zero-Day?**

A Non-Zero-Day is a day where you do anything, no matter how big or small, towards your goal.
For example if your goal is "to get in shape", doing one push-up counts as a Non-Zero-Day (as do 50 of course).
You will find your motivation increases as you build a string of Non-Zero-Days!


**Technologies used**

- sqlite3
- Python


**How does it work?**

**register**
The user can register by providing the following:
- Username: Of course this needs to be unique.
- Password: Must be at least 8 digits long and include at least one number and symbol, it will be hashed once accepted.

**login**
After creating an account you will be able to log in and make full use of the webpage.
This is done using sessions.

**Index / Forgive / Activity**
Once logged in, the webpage will check wether you already provided an activity that day.
This is done via a single record SQL table that checks the current_date continuously.

If you already logged an activity it will encourage you and ask you to come back tomorrow.
if not it will ask you:

"Was today a Non-Zero-Day?".

If you answer yes you will be able to add an activity which will be stored in a table, log your last activity date, add a day to your streak and compare the amount to your current record.
If you answer no you will receive a message to reassure you. Remember that it's important to forgive yourself, we all have off-days.
You'll also be informed that the day is not over and that you can still turn it around.

**Philosophy**
A page describing the philosophy of Non-Zero-Days.
This is just informative.

**Goals**
On this page you can add goals, remove them or mark them as "completed".
Once completed they will be added to your progress page.

**Progress**
On this page you can see your current Non-Zero-Day streak. Be careful because it will reset if you don't log an activity for an entire day.
You can also see your personal record which represents the highest streak you've held, this is meant to be a motivation if your streak ever resets
as it gives you something additional to strive for.

You will also see a list of your completed goals which are pulled from an SQL table and implemented via jinja2.
You can also reset completed goals to "active". For example if you wanted to lose 5 pounds but regained them, you could reset this goal.

You will also see a list of actions that you have performed over the past week.


**Possible improvements**
These are things that could be added on a future version:
- Add a calendar that will display activities.
- Ability to change account details.
- Notifications (via email) when the day is almost over.
