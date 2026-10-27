# Outreach plan, Week 4

## Rules I am holding myself to

One message per organisation, written by hand, sent by hand. No automation, no mailmerge, no sending the same text to a list. If someone says no, or does not reply, that is the end of it and nothing follows.

I am an intern with a small piece of evaluation work, not a salesperson with a product. The message says exactly that. If a conversation ever gets as far as actual paid work, it goes through SafeX Solutions rather than through me, and I will say so in the call rather than after it.

One thing I will not do: imply I have studied their operation. I have not. The work is an evaluation of three model vendors against a courier support use case I built for Week 3. Pretending otherwise would be the fastest way to waste someone's time and lose the meeting.

## Who I am approaching and why

Three e-commerce logistics companies in Pakistan, all of them tech-forward enough to already be thinking about support automation, and all small enough that a comparison like this is useful rather than something they have already paid a consultancy for.

**PostEx.** Courier plus payments for e-commerce sellers, so their support load carries both delivery questions and money questions. The cash-on-delivery cases in my eval set are exactly the kind of message they field, and the escalation rules I tested are the ones that matter when money is disputed.

**Rider (withrider.com).** Karachi-based last-mile, built around online shippers, founded 2019, tech-led enough to have an API-first posture. Their volume is high enough that per-contact support cost is a real line item.

**Unity Retail.** Sells fulfilment software to merchants rather than delivering parcels itself, so their support conversations are with sellers, not consumers. Different message mix, same triage problem, and a company whose customers would feel the benefit twice over.

Before sending anything, I find the actual person who owns customer operations or support at each company on LinkedIn and address them by name. A message sent to a generic inbox is a message nobody owns.

## Message 1: PostEx

Channel: LinkedIn direct message, to whoever owns customer operations.

> Hi there,
>
> I am Fatima Naseer, an intern at SafeX Solutions and a computer science student at the Institute of Space Technology. I spent this week running a small evaluation on something I think sits close to your day job.
>
> I built a test set of thirty real-shaped customer support messages for a courier business, in Roman Urdu, English, and the mix people actually type, then ran the same prompt through three language model providers and scored them on how well they labelled intent, pulled out tracking numbers and cash-on-delivery amounts, and answered without inventing a delivery date they had no way of knowing. That last one turned out to be the measure that separates them.
>
> I am not selling anything and I have no product. I am reaching out because you would know within five minutes whether my test cases match what your support team actually sees, and that would make the work considerably better than it is now.
>
> If you have twenty minutes in the next two weeks, I would happily walk you through what I found and hear where I got the picture wrong. No obligation, and if this is not useful, please just say so and I will not follow up.
>
> Fatima

## Message 2: Rider

Channel: LinkedIn direct message.

> Hi there,
>
> I am Fatima Naseer, a computer science student at the Institute of Space Technology, currently interning at SafeX Solutions.
>
> This week I compared three language model providers on one narrow job: reading an inbound courier support message and deciding what it is, what to pull out of it, and whether a human needs to see it. Thirty hand-labelled cases, the same prompt to all three, scored on accuracy, cost per thousand calls, response time at the ninety-fifth percentile, and how much work each API was to integrate.
>
> The gap that surprised me was not accuracy. It was how often a model would confidently tell a customer where their parcel was, when it had no access to any tracking data at all.
>
> I am not pitching a service. I would like twenty minutes to show you the comparison and ask whether the failure modes I found are the ones that would actually cost you money, because right now that is my guess and not much more. Happy to send the report first if you would rather read than talk.
>
> If it is not a fit, no problem at all, and I will leave it there.
>
> Fatima

## Message 3: Unity Retail

Channel: LinkedIn direct message, or the contact form on the site if no individual is findable.

> Hi there,
>
> I am Fatima Naseer, an intern at SafeX Solutions, studying computer science at the Institute of Space Technology.
>
> I have just finished a vendor comparison of three language model providers for one specific task: first-line triage of support messages in a logistics setting. Because your customers are sellers rather than end consumers, I suspect the message mix you see is quite different from the one I built my test set around, and that difference is the interesting part.
>
> Would you have twenty minutes for me to show you the method and the results, and to ask what your support conversations actually look like? I am not selling anything, and the work is already done either way. I am after the reality check.
>
> If now is not a good time, or this is not relevant, just say and I will not write again.
>
> Fatima

## After sending

Every message gets a row in `trackers/Week4_Outreach_Tracker.xlsx` on the day it goes out: organisation, platform, date, and what came back, including silence. A no goes in the tracker as a no and the row closes there.

If someone agrees to a call, the same three things go into it every time: what the test set is, what the numbers say, and where the method is weak. The third one is the reason anyone would take a second call.
