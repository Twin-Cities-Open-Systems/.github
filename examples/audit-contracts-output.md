# Contract ratification audit -- 10 kind:Contract file(s) across 2 repo(s)

- NO_STATUS_FIELD: 4
- OTHER_STATUS: 1
- NEEDS_VOTE: 1
- RATIFIED_VERIFIED: 4

## Needs a vote / a human call

- **NO_STATUS_FIELD** `Twin-Cities-Open-Systems/fleet-ops/hee/contracts/fleet.dir-layout.contract.v1.yaml` -- spec.status is entirely absent -- not even declared proposed
- **NO_STATUS_FIELD** `Twin-Cities-Open-Systems/human-execution-engine/hee/contracts/hee.fleet-hosts.contract.v1.yaml` -- spec.status is entirely absent -- not even declared proposed
- **NO_STATUS_FIELD** `Twin-Cities-Open-Systems/human-execution-engine/hee/contracts/hee.kind-registry.contract.v1.yaml` -- spec.status is entirely absent -- not even declared proposed
- **NO_STATUS_FIELD** `Twin-Cities-Open-Systems/human-execution-engine/hee/contracts/hee.validation-gates.contract.v1.yaml` -- spec.status is entirely absent -- not even declared proposed
- **OTHER_STATUS** `Twin-Cities-Open-Systems/fleet-ops/hee/contracts/fleet.gpg-cross-signing.contract.v1.yaml` -- status: 'completed' -- different vocabulary than ratified/proposed, needs a human call on how to classify it
- **NEEDS_VOTE** `Twin-Cities-Open-Systems/fleet-ops/hee/contracts/spencer.touchy.financial-authority.contract.v1.yaml` -- awaiting: ['spencer']

## Ratified and verified (evidence file confirmed live)

- `Twin-Cities-Open-Systems/fleet-ops/hee/contracts/nuc1-claude.claudeops-j1.hire-authority.contract.v1.yaml`
- `Twin-Cities-Open-Systems/fleet-ops/hee/contracts/nuc1-claude.claudesec-j1.hire-authority.contract.v1.yaml`
- `Twin-Cities-Open-Systems/fleet-ops/hee/contracts/nuc1-claude.touchy.peer-authority.contract.v1.yaml`
- `Twin-Cities-Open-Systems/fleet-ops/hee/contracts/spencer.nuc1-claude.senior-authority.contract.v1.yaml`

## Legacy contracts/ family (different schema, not scored)

See `contracts/README.md` in human-execution-engine -- these govern GPT/Oper/Relay lanes, not authority/ratification. Listed for visibility only:

- `Twin-Cities-Open-Systems/human-execution-engine/contracts/agent-instance-signature-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/dric-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/hee-schema-id-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/hee-sqz-roll-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/outfile-evidence-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/roles-trilateral-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/shift-metrics-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/shift-schedule-v1.contract.yaml`
- `Twin-Cities-Open-Systems/human-execution-engine/contracts/validator-contract-v1.contract.yaml`

