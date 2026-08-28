# CanteenFlow AI

**Beat the Queue. Predict the Rush. Eat Smarter.**

An AI-powered campus canteen ordering platform: multi-vendor pre-ordering, smart
pickup scheduling, real-time order tracking, group ordering with split payment,
SmartSwap food-waste reduction, and an AI-driven vendor dashboard (demand
forecasting, smart batching, Canteen Copilot).

This is a **frontend prototype** — all data lives in React state for the demo.
There is no real backend, database, or payment processor wired in (see
"Current limitations" below).

---

## 1. Running the project

Requirements: Node.js 18+ and npm.

```bash
npm install
npm run dev
```

Then open the URL Vite prints (usually `http://localhost:5173`).

To build a static production bundle:

```bash
npm run build
npm run preview
```

---

## 2. Demo accounts

Two accounts are seeded automatically so you can log in immediately:

| Role    | Email                | Password     |
|---------|-----------------------|--------------|
| Student | alex@campus.edu       | alex123      |
| Vendor  | canteen@campus.edu    | canteen123   |

You can also register a brand-new account from the auth screen (choose
Student or Vendor; vendors also pick which canteen they manage).

---

## 3. Testing student mode

1. Log in as the student demo account (or register a new student account).
2. **Home** — see crowd level, estimated queue, and today's popular food.
3. **Vendors** — pick a canteen, browse/search the menu, add items to cart.
4. Open the cart → see the **AI Suggestion** for a better pickup slot →
   accept or keep the original slot.
5. Click **Continue to Payment** → choose UPI / Card / Wallet → **Pay**.
   This is a simulated payment (no real transaction). After a short
   "processing" delay you'll see a **Payment Confirmed** screen with a
   payment slip / coupon: a large order number, a QR-style code, itemized
   total, and pickup counter — this is what you'd show at the counter.
6. **Orders** tab — track the order live as it moves through
   Order Placed → Payment Confirmed → Order Accepted → Preparing →
   Almost Ready → Ready for Pickup (simulated automatically over ~10s).
   Tap **View slip** on any order to see the payment slip again.
7. **Group Orders** — see a simulated split-bill flow with friends.
8. **SmartSwap** — claim or donate an order another student can't collect.
9. **Eco Points** — see your balance and how points were earned.
10. **Notifications** — all order-status pushes land here.

## 4. Testing vendor mode

1. Log out, then log in as the vendor demo account (or register a vendor
   account and pick a canteen to manage).
2. **Dashboard** — today's orders, revenue, active orders, charts
   (orders by hour, revenue by day, popular food, demand forecast).
3. **Live Orders** — orders currently in the kitchen.
4. **Smart Batches** — similar orders grouped for efficient prep.
5. **Demand Forecast** — AI-labeled predicted demand per food item with
   prep recommendations.
6. **Inventory** — mark items Available / Low stock / Sold out; shortage
   warnings appear automatically.
7. **Food Waste** — sustainability stats (orders saved, meals donated/swapped).
8. **Canteen Copilot** — click a preset question (busiest time, most
   popular food, what to prepare, etc.) to get an AI-style answer.

## 5. Access control

- Role is decided at login/registration and can't be changed from inside
  the app — a student account only ever opens the student workspace, and
  a vendor account only ever opens the vendor workspace (scoped to the
  canteen they registered for).
- There's an explicit **Log out** button in the top nav; there's no way to
  jump between roles without signing out and back in as a different account.

---

## 6. Current limitations (this is a demo, not production)

Because there's no backend in this scaffold, please be aware:

- **Accounts and orders reset on page refresh** — everything lives in
  React state for the session only.
- **Passwords are compared in plain text in the browser.** This is fine
  for a hackathon demo but must never be done in production. A real
  deployment should authenticate against a proper backend (e.g. Supabase
  Auth) with hashed passwords and server-side session tokens.
- **Payments are fully simulated** — no real payment gateway (Razorpay,
  Stripe, etc.) is integrated.
- **The "access control" is UI-level only** — a technically determined
  user could still inspect client-side code. Real role security requires
  server-side enforcement (e.g. Supabase Row Level Security) so the
  backend — not just the UI — refuses cross-role data access.

### Suggested next step: wiring up Supabase

To make this production-ready:
1. Create a Supabase project and enable email/password auth.
2. Create tables for `users`, `vendors`, `menu_items`, `orders`,
   `order_items`, `payments`, `group_orders`, `demand_predictions`,
   `notifications`, `inventory`, and `eco_points` (see the original
   product spec for the full schema).
3. Add Row Level Security policies so students can only read/write their
   own orders, and vendors can only read/write orders and inventory for
   their own canteen.
4. Replace the in-memory `users`/`orders` state in `src/App.jsx` with
   Supabase queries and Realtime subscriptions.
5. Integrate a real payment gateway in test/sandbox mode for the payment
   step.

---

## Tech stack

- React + Vite
- Tailwind CSS
- lucide-react (icons)
- Recharts (charts)
