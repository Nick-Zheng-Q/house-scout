# Rental checks

For the relevant jurisdiction and native terms, read [market guidance](international-markets.en.md); for period conversion, cash, transport passes and financing assumptions read [cost calculations](cost-comparison.en.md). Mainland China platform steps remain in [platforms](platforms.en.md).

Distinguish whole-unit, room, bedspace, managed apartment, and sublet. Confirm exclusive/shared space, occupants, pets, visitors, facilities, furniture, parking and storage. “Move-in ready” does not prove an inventory, repairs, or included internet. Verify the lessor's right to let and any sublet/agent authority and duration; an online claim is not a document or identity check.

Record availability, lease start and rent-free period, minimum term, payment frequency, increases/renewal, sublet limits, early exit, deposit return, repairs, and handover. A long lease is not automatically flexible. A refundable deposit still ties up cash and may be disputed.

Use one monthly basis for rent and essential management, utilities, heating/cooling, internet, parking and other charges. Unknown usage means a range/unknown, not zero. Separately show one-time agent/service/cleaning/moving fees, deposit, prepaid rent, discount conditions and later normal price. Keep three figures distinct:

1. **Known monthly subtotal + unknown necessary items.**
2. **Nonrefundable upfront fees + refundable deposit, excluding prepaid rent.** `python3 scripts/check_rentals.py <input.json>` verifies entered arithmetic and hard-condition states; see [input](check-input.en.md).
3. **Cash due at signing/move-in:** itemize only payments evidenced as due then. The script's `signing_amount` helps arithmetic, but an unknown payment date or omitted charge prevents a complete-cash conclusion.

An advertised rent is not all-in. Unapproved discounts, subsidies, bargaining, and public-housing eligibility are conditional scenarios, not reductions to the base budget. Before payment, verify the unit, lessor/agent authority, payee, inventory and relevant local contract/registration rules. Large prepayment demands, refusal to show the unit/authority, or pressure for nonrefundable fees call for pausing and checking—not a definitive accusation of fraud.
