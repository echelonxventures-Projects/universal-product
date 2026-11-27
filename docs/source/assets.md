# Fixed assets — the parts only a person can write

## Flows

**Registering an asset.** An asset is something the business owns and uses for years: computers,
furniture, a vehicle, machinery, a building, software. It has a cost, a residual value (what it will
be worth at the end), a useful life in months (its category's usual life unless you set one) and a
depreciation method. Registering it puts its cost on the books, paid from the bank or owed to a
supplier.

**Depreciation.** From the month it comes into service, the asset depreciates each month: by
**straight line**, the same amount every month, or by **declining balance**, a fixed share of what
is left, switching to straight line when that charges more. It never goes below its residual value,
and the last month takes exactly what is left. Each month is posted once. The platform posts every
month as it ends; staff can post up to any month that has begun.

**Selling or writing off.** An asset sold or written off on a day is first depreciated to that
month. Its cost and depreciation then come off the books. The difference between what it was sold
for and its book value is posted as a gain or a loss. A write-off has no proceeds.

## Manual: store_admin

Open **Payments & Finance → 🏷️ Fixed Assets**. Your role needs the fixed assets section; the Finance
role has it.

- **Register an asset**: name, category, cost, residual value, life (left empty, the category's),
  method, the day it was bought and how it was paid.
- **Depreciation**: choose a month and **Post depreciation**. Months already posted are left alone.
- Open an asset to see every month of its schedule, posted or to come, and to **Sell or write off**
  it, saying why.
- The register shows each asset's cost, depreciation to date and book value, with totals by category.
