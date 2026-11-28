# Mobility — the parts only a person can write

## Flows

**Asking for a ride.** A signed-in rider says where from and where to. A pickup can be the rider's
own position ("Use my location") or one of the places the store names; with both points on the map
the rider sees the price before asking. The nearest free driver of that kind of vehicle is matched,
by the position their phone last reported. A rider has one ride under way at a time.

**Sharing a ride.** A rider who chooses to share pays less. Riders in the same kind of car who are
picked up near each other and dropped near each other share one driver, until someone is on board or
the shared ride's time to form is up. The driver stays busy until the last rider is dropped.

**Booking for later.** A ride can be booked between half an hour and 30 days ahead, with an
estimate. It is cancelled free while it waits. Shortly before the time it becomes the rider's ride
and a driver is matched. A booking the platform could not reach in time is marked missed rather
than sent late.

**On the trip.** The rider follows the driver on a small map, with the time to the pickup and then to
the drop. A finished trip's distance and time come from the driver's track, and the fare from the
store's rates. Rides waiting for a driver are given one as soon as a driver comes free.

**Safety.** The rider can send someone a private link that shows the ride's progress, the driver's
first name and car, and where they are. The link closes a while after the ride. Riders and drivers
have an emergency button: it alerts the store at once with where they are, and shows the local
emergency number. After a trip either side can report an incident or something left in the car.

**Ratings and tips.** After a trip the rider rates the driver and the driver rates the rider, once
each, within a week. A driver whose recent average falls below the store's minimum to dispatch is
held out of dispatch until the store looks into it. A rider can tip once on a finished ride.

**Driver pay.** Each trip earns the driver its fare less the platform's share, plus any tip. A
cancellation fee counts as a trip. A payout takes every unpaid trip up to a day. Someone other than
whoever made it approves it, which puts it on the books as owed to the driver, and it is then marked
paid.

## Manual: store_admin

Open **Mobility**. Your role needs the rides, fleet or trips section; the Dispatch & Safety role has
all three, and Finance has trips for driver pay.

- **🚗 Rides & Dispatch** and **🚙 Fleet & Drivers**: rides, surge zones, drivers and vehicles. A
  driver signs in to the driver's page with the email you give them here.
- **🛡️ Trips, Safety & Pay**:
  - **Safety reports**: open emergencies are shown first, in red. **I'm on it** takes one;
    **Resolve** closes it with what happened. Call the emergency number shown if anyone is in
    danger.
  - **Booked for later** and **Shared rides forming**: what is coming up. **Dispatch what is due
    now** sends due bookings at once.
  - **Drivers to review**: drivers whose ratings fell below the floor. **Let them drive** clears the
    hold once you have spoken to them.
  - **Driver pay**: **Make payout** for a driver up to a day, **Approve** (not your own), then **Mark
    paid** with the bank's reference. **Void** frees an unpaid payout's trips. **Statement** shows
    each trip.
  - **Places riders pick from**: one per line, `name, latitude, longitude`.

## Manual: store_staff

With the Dispatch & Safety role, handle safety reports, bookings and drivers to review as above.
With the Finance role, make, approve and pay driver payouts. You cannot approve a payout you made.

## Manual: shopper

Open **Rides** from the footer and sign in. Type where from and where to, or use your location or a
named place; **See the price**, then **Ask for a ride**. Tick **Share the ride** to pay less, or
**Book for later** to choose a time. While the ride is under way you see your driver, their car's
plate and the map. **Share my trip** gives you a link to send to someone you trust. **🚨 Emergency**
alerts the store at once; call the number shown if you are in danger. Afterwards, rate your driver,
add a tip, or report a problem.

## Manual: driver

Open **Drive** from the footer and sign in with the email the store has for you. **Go online** and
allow the page to use your position; riders see you on their map and you are matched to rides near
you. Each ride shows the next step (arrived, start the trip, drop off). Rate your riders afterwards.
**🚨 Emergency** alerts the store at once. **Earnings** shows each trip's fare, the platform's share,
tips and what you keep, and your payouts.

## Manual: guest

Someone who was sent a ride's link sees its progress, the driver's first name, the car and the map,
without signing in. The link stops working a while after the ride ends.
