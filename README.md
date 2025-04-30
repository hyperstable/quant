# Hyperstable quantitative models

This directory stores quantitative models and sheets that have been used to test mechanism design.

## Interest rate models

Hyperstable applies different interest models:

- Morpho-based adaptive interest rate
- Canto- and peg-based interest rate

### Notes: Adaptive interest rate

The original Morpho adaptive interest rate uses the utilization as a measure to adapt their interest rate.
This utilization is limited to a range between zero and one.
In order to use the same equations, we had to transform the metrics that we see as important (collateral ratio) to a range that fits the Morpho equations.

The adaptive behavior of this rate is as follows:

1. If the collateral ratio drops below our vault-specific target, we want to increase the interest rate
2. If the collateral ratio rises above our vault-specific target, we want to decrease the interest rate

The mapping to a range between zero and one can be achieved by using loan-to-value (LTV) values instead of collateral ratios.

## Link ERC20 HyperCore <> HyperEVM

The deploy spot script is a script that deploys the spot contract on HL. It uses the following parameters in an `.env` file:

```bash
PRIVATE_KEY="0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
DEPLOYER="0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
TOKEN_ID=1
CREATION_NONCE=0
TOKEN_CONTRACT_ADDRES="0xdeadbeefdeadbeefdeadbeefdeadbeefdead"
```
