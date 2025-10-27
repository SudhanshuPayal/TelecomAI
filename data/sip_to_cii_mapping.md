# **SIP to CII Mapping (Internal Reference)**

This document maps standard SIP protocol messages to their corresponding ATIS CII message types.

| SIP Method / Response | Call Flow Event | CII Message(s) |
| :---- | :---- | :---- |
| INVITE | (Originating) | Origination |
| 180 Ringing | (Terminating) | TerminationAttempt |
| 183 Session Progress | (Terminating) | TerminationAttempt |
| 200 OK (for INVITE) | (Terminating) | TerminationAnswer |
| 486 Busy Here | (Terminating) | TerminationFailure (Reason: Busy) |
| 487 Request Terminated | (Terminating) | TerminationFailure (Reason: No Answer) |
| BYE | (Either Party) | Release |
| REFER | (Transferor) | Transfer (Initiation) |
| NOTIFY | (Transferee) | Transfer (Completion) |
| HOLD | (Party) | Hold |
| RESUME | (Party) | Resume |

