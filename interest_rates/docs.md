## Hyperstable interest model

This document describes the interest rate model as used within Hyperstable.
We list details about the following components:

- Manual interest ($$r_m$$)
- Peg-based interest ($$r_p$$)
- Adaptive interest ($$r_a$$)


The total interest rate ($$r$$) is obtained as sum of all individual parts.

$$
r = r_m + r_p + r_a
$$

### Manual interest rate

The manual interest rate is static and set by the protocol as a constant value and represents the minimum interest rate that the protocol collects.

$$
r_m = c
$$

This interest rate acts across all collateral vaults.

### Peg-based interest rate

The peg-based interest rate is dynamic and set according to the current Hyperstable USD (USH) peg.
If the stablecoin trades below the 1 USD peg, the interest increases based on the following formula:

$$
r_p^n = max(0, \Delta \alpha + r_p^{n-1}),
$$

where $$\Delta$$ represents the absolute difference from the 1 USD peg, and $$\alpha$$ represents a scaling coefficient.
This interest rate uses the previous interest rate $$r_p^{n-1}$$ in step $$n$$. Updates are restricted by a time lock that hinders manipulation attempts.
Once updated, the time lock rejects new attempts to update the interest rate for time range $$t$$.
This interest rate acts across all collateral vaults.

### Adaptive interest rate

The adaptive interest rate is dynamic and set according to the current collateralization of a specific vault.
For this interest rate the adaptive interest rate as known from Morpho Blue is adjusted to fit our CDP model.
This interest model maps utilization to interest rates and partitions the utilization into two categories based on a defined target ($$t$$):

- Utilization falls below target: curve continously shifts downwards
- Utilization exceeds target: curve continously shifts upwards

The speed at which the curve adjusts is based on the distance of the current utilization to the target.
This incremental adjustment of the curve allows for rate exploration, stabilizing when the interest rate aligns with the market equilibrium.

Morpho Blue uses the ratio of borrowed assets to the total supply of the vault.
However, since our collateral debt position (CDP) protocol needs to have a collateral ratio that succeeds 100\%, the utilization calculation needed to be redefined to fit onto a range between 0 and 1.

#### Hyperstable utilization model

We define the minimum loan to value ($$mLTV$$) as the inverse of our minimal collateral ratio ($$mCR$$).

$$
mLTV = 1.0 / mCR
$$

We obtain the loan to value (LTV) of the current vault as follows

$$
LTV = \beta / \gamma,
$$

where $$\beta$$ represents the total USH debt of the vault and $$\gamma$$ represents the collateral market value in USD.
The utilization ($$u$$) is calculated as follows

$$
u = clamp(LTV / mLTV, 0, 1),
$$

where we normalize the $$LTV$$ by $$mLTV$$ and enforce a range $$r \in [0, 1]$$ through clamping to that range *via*

$$
clamp(val, min\\_val, max\\_val) = max(min(val, max\\_val), min\\_val).
$$

#### Error function

We use the utilization to calculate an error factor based on where the current utilization is based at.
The error normalization factor ($$e_n$$) is 

$$
e_n = 1.0 - t,
$$

if the current utilization exceeds the target and else

$$
e_n = t.
$$

This is used to calculate the error factor

$$
e = \frac{u - t}{e_n}
$$

#### Adaptive curve

We use the rate at target ($$r_t$$) and the error factor ($$e$$) to calculate points on the curve.
For this, we define

$$
\theta = 1.0 - 1/\omega,
$$

if the error factor is below zero and else

$$
\theta = \omega - 1
$$

and calculate the point on the curve

$$
p = (\theta e + 1) r_t.
$$

Here, $$\omega$$ represents the steepness of the curve.

#### Rate at target

A new rate at target is obtained from the start rate ($$r_s$$) and the linear adaption ($$l_a$$) clamped between minimum ($$r_{min^t}$$) and maximum ($$r_{max^t}$$) rates at target

$$
r_t = clamp(r_s exp(l_a), r_{min^t}, r_{max^t}).
$$

#### Adaptive interest rate

The adaptive interest rate is calculated as follows:

1. Obtain vault utilization by providing the collateral value in USD, the total USH debt of the vault, and the minimum collateral ratio of the vault
2. Calculate the error factor using the current utilization and the target utilization
3. Get the start rate and check if this is the model initialization
4. If initialization then use static values otherwise calculate the linear adaptation, calculate the point on the curve, and set the new rates

An example implementation in Python can be found [here](interest_rates/adaptive_irm/adaptive_irm.ipynb)
