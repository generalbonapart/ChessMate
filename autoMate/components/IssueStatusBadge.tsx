import { Status } from '@prisma/client'
import React from 'react'
import { Badge } from '@radix-ui/themes'

const statusMap: Record<Status, {label: string, color: 'red' | 'violet' | 'green'}> = {
    OPEN: {label: 'Open', color: 'red'},
    IN_PROGRESS: {label: 'In Progress', color: 'violet'},
    CLOSED: {label: 'Closed', color: 'green'}
};

interface Props{
    status: Status
}

const IssueStatusBadge = ({status}: Props) => {
  return (
    <Badge color={statusMap[status].color}>
        {statusMap[status].label}
    </Badge>
  )
}

export default IssueStatusBadge