# Contract: the steps that trust the mirrors' keys, and the collection they need

## `requirements.yml`

- Asks for `infrastructurebuilder.csis_spack` `>=0.0.3,<0.1.0`, with a comment
  saying that 0.0.3 is the first to answer Spack's confirmation for the keys
  mirrors publish.
- `just init`, run where 0.0.2 is installed, leaves 0.0.3 installed.

## The three `from_mirrors` steps

On a node with the collections `requirements.yml` asks for:

| Run | Result |
| --- | --- |
| mirrors that publish a key not yet trusted | no prompt; the key trusted and reported as such (`changed`) |
| the same again | no prompt; no change |
| check mode | nothing run; no change |
| no binary mirror configured | fails as Spack does (the collection's behaviour) |

## Never

- runs `spack buildcache keys` through the generic `command` step;
- applies with a collection older than 0.0.3.
