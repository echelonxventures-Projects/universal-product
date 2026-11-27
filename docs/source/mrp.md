# Material requirements planning — the parts only a person can write

## Flows

**Bills of materials.** An item that is made has a bill of materials: the components one unit takes,
and the share lost in making it. A component may be made from its own components, to any depth, but
never from the item itself; such a bill is refused. An item without a bill is bought.

**Planning settings.** Each item may have a lead time in days (otherwise its supplier's for a bought
item, or the default), a safety stock to keep and a smallest lot.

**What must be ready.** The master schedule lists what must be ready by a date. Open work orders add
what they still need of their components.

**A planning run.** A run looks a number of days ahead and takes items level by level, from finished
goods down to raw materials. For each, what is needed plus its safety stock, less what is on the
shelf and what open purchase orders and work orders will bring, is what must still be made or bought,
raised to the smallest lot or the supplier's minimum order. A made item becomes a planned work order,
and its components are needed when that order must start. A bought item is ordered from its primary
supplier. Each suggestion says when it must be ordered or started; one whose date has passed is late.

**Making the orders.** Suggestions become draft purchase orders, one per supplier, and planned work
orders carrying their components. Each suggestion is acted on once. An item with no supplier is not
ordered. The next run counts what those orders will bring; a new run replaces suggestions nobody
acted on.

## Manual: store_admin

Open **Business Operations → 🏭 Planning (MRP)**. Your role needs the mrp section; the Planning role
has it.

- **Bill of materials**: type the item's code and **Show**. Write one component a line as
  `item code | quantity | % lost`, then **Save the bill**.
- **Planning for an item**: its lead time, safety stock and smallest lot.
- **What must be ready**: add what must be ready by when.
- **Plan**: **Run planning**, check what it suggests, dismiss what you will not do, then **Make the
  orders**. Purchase orders are drafts to check and send under Purchasing.
