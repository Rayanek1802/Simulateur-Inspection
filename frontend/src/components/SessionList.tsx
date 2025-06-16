import React, { useState, useEffect, useCallback } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Link,
  Text,
  useToast,
} from '@chakra-ui/react';
import axios from 'axios';

interface Session {
  id: number;
  date: Date;
  students: { name: string }[];
}

const SessionList: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const toast = useToast();
  const API_URL = process.env.REACT_APP_API_URL;

  const fetchSessions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/sessions/`);
      setSessions(response.data);
    } catch (error) {
      toast({
        title: 'Erreur',
        description: 'Erreur lors du chargement des sessions',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  }, [toast]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  if (sessions.length === 0) {
    return (
      <Box>
        <Heading size="lg" mb={6}>Evaluation Sessions</Heading>
        <Text>Aucune session trouvée.</Text>
      </Box>
    );
  }

  return (
    <Box>
      <Heading size="lg" mb={6}>Evaluation Sessions</Heading>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>DATE</Th>
            <Th>STUDENT</Th>
            <Th>ACTIONS</Th>
          </Tr>
        </Thead>
        <Tbody>
          {sessions.map((session) => (
            <Tr key={session.id}>
              <Td>{new Date(session.date).toLocaleString()}</Td>
              <Td>{session.students && session.students.length > 0 ? session.students[0].name : ''}</Td>
              <Td>
                <Link
                  as={RouterLink}
                  to={`/session/${session.id}`}
                  color="blue.500"
                >
                  View details
                </Link>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default SessionList; 