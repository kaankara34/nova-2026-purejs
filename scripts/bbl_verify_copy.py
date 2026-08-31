"""Verify every line of the supplied Build Beyond Living copy appears verbatim in the built page."""
import html
import pathlib
import re

page = (pathlib.Path(__file__).resolve().parent.parent / "frontend" / "build-beyond-living.html").read_text(encoding="utf-8")
main = page.split('<main class="bb" id="bbMain">', 1)[1].split("</main>", 1)[0]
text = re.sub(r"<[^>]+>", "\n", main)
text = html.unescape(text)
text = re.sub(r"[ \t]+", " ", text)
lines = {ln.strip() for ln in text.split("\n") if ln.strip()}
blob = " ".join(sorted(lines))

APPROVED = """NOVA
BUILD BEYOND LIVING
A residence is more than where life takes place.
It is part of the way life feels.
A WAY OF LIVING
The home is only the beginning.
A well-designed residence can change the way a day begins, but living well extends beyond the rooms themselves.
It is the ease of arriving home. Knowing that help is available when something needs attention. Having spaces that support work, wellbeing and time with others. Being able to arrange the small things without allowing them to interrupt the day.
Nova brings these parts together as one residential experience.
Not more for the sake of more.
Simply a better way for things to work.
EVERYDAY, CONSIDERED
The things that make life easier rarely need to be complicated.
A technical issue at home.
A restaurant reservation.
A guest arriving.
A shared space to book.
A question that needs an answer.
These are ordinary moments.
The difference is how easily they are resolved.
At Nova, service is part of the residential experience from the moment a resident moves in.
NOVA MEMBERSHIP
Your residence.
Your services.
One connection.
Nova Membership brings the services around your home into one place.
From concierge requests and technical support to amenity bookings and everyday reservations, residents can manage what they need directly through the Nova Membership experience.
It is designed to remove small interruptions from everyday life and keep access to Nova simple, direct and personal.
Available exclusively to Nova residents.
Good evening
Quick Access
Concierge
Technical Support
Amenities
Reservations
Your Requests
Restaurant Reservation
In Progress
Home
Services
Support
CONCIERGE
A direct line to everyday assistance.
Nova Concierge helps residents with the practical details that sit outside the home itself — from a reservation to a request that simply needs arranging.
Make a Request
Transportation
Guest Assistance
Other Request
TECHNICAL SUPPORT
Help when your home needs it.
Technical requests can be submitted directly through Nova Membership, making it easier to report an issue, follow its status and stay in contact with the relevant team.
New Request
Active Requests
Completed Requests
Air Conditioning
Status: In Progress
AMENITIES
Shared spaces, without the back and forth.
Residents can view availability and reserve eligible social and recreational spaces directly through the application.
Private Lounge
Meeting Room
Cinema Room
Padel Court
Golf Simulator
View Availability
Reserve
LANDSCAPE & HOME SERVICES
The details around home, taken care of.
Where available, gardening, landscape-related requests and selected residential services can be organised through Nova Membership.
Home Services
Garden Assistance
Maintenance Request
Schedule Service
RESERVATIONS
From home to the city.
Need a table for dinner? Residents can send restaurant and selected reservation requests through Nova Concierge without having to manage every detail themselves.
Restaurant
Date
Time
Guests
Request Reservation
Concierge Confirming
RESIDENT SUPPORT
Nova stays within reach.
Questions, requests and follow-up do not need to begin with finding the right person. Nova Membership gives residents a direct point of contact after handover as well.
Messages
Request History
Contact Nova
BEYOND THE APARTMENT
Some of the best rooms may not be inside your home.
The spaces shared by residents are approached with the same attention as the residences themselves.
A place to exercise.
A room to work.
Somewhere to meet.
A quiet hour in the spa.
A cinema without leaving home.
A garden that becomes part of the day.
Amenities are not added to complete a list.
They are there to make the building more useful to the people who live in it.
RESIDENTIAL HOSPITALITY
Service should be present without becoming visible.
The best service does not make daily life feel managed.
It simply removes friction.
A question is answered.
A request reaches the right person.
A guest is expected.
A reservation is being handled.
Something at home needs attention and the process has already started.
That sense of ease is part of what Nova means by living beyond the residence itself.
Available when needed.
Quiet when it is not.
THE NEIGHBOURHOOD
A good home becomes part of a good life around it.
Where you live shapes more than the journey home.
It is the places you return to, the streets you know, dinner close by, a morning walk, time by the coast or an evening with friends a few minutes away.
Nova develops residences within established neighbourhoods where the city already has a rhythm of its own.
The aim is not to separate residents from that life, but to make the connection to it feel effortless.
Close to the city.
At home in the neighbourhood.
BEYOND HANDOVER
The relationship should not end when the keys are delivered.
A building changes after people move into it.
Homes are used, questions arise and the needs of residents continue.
For Nova, completion is not the point at which the relationship disappears.
Resident support, technical assistance and the Nova Membership experience keep that connection open beyond handover.
A residence is delivered once.
Living in it happens every day.
We build the home.
Then we think beyond it.
Beyond the plan is comfort.
Beyond the building is service.
Beyond the private residence are spaces to meet, work, exercise and unwind.
Beyond handover is an ongoing relationship.
And beyond all of them is the way a place becomes part of everyday life.
That is what Build Beyond Living means at Nova.
Not simply a residence.
A way of living around it.
Explore Nova Residences
Discover Nova Membership
"""

missing = []
checked = 0
for raw in APPROVED.strip().split("\n"):
    want = raw.strip()
    if not want:
        continue
    checked += 1
    # headings/eyebrows are uppercased through CSS, so compare case-insensitively
    if want in lines or want.lower() in {l.lower() for l in lines}:
        continue
    if want.lower() in blob.lower():
        continue
    missing.append(want)

print("checked", checked, "approved lines")
if missing:
    print("MISSING", len(missing))
    for m in missing:
        print("  -", m)
else:
    print("ALL PRESENT")
