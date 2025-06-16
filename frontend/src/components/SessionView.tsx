import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Button,
  Heading,
  VStack,
  Text,
  useToast,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  FormControl,
  FormLabel,
  ModalFooter,
  Input,
  Checkbox,
  HStack,
  Divider,
  Select,
  Badge,
  CheckboxGroup,
  Stack,
  FormHelperText,
} from '@chakra-ui/react';
import axios from 'axios';

interface Observation {
  id: number;
  text: string;
  timestamp: Date;
  ob_code: string | null;
  competence: string | null;
  is_checked: boolean;
  student_name: string;
}

interface Exercise {
  id: number;
  name: string;
  date: Date;
  is_completed: boolean;
  observations: Observation[];
  competences: string[];
}

interface StudentData {
  name: string;
}

interface Session {
  id: number;
  date: Date;
  students: StudentData[];
  exercises: Exercise[];
}

interface Report {
  [studentName: string]: {
    report: {
      [competence: string]: {
        how_many: number;
        how_often: number;
        safety_score: number;
        final_grade: number;
        observations: { ob_code: string | null; text: string }[];
      };
    };
    unchecked_observations: { text: string; ob_code: string; competence: string }[];
  };
}

const COMPETENCES = ['PRO', 'COM', 'FPA', 'FPM', 'KNO', 'LTW', 'PSD', 'SAW', 'WLM'];

const SessionView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<Session | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [safetyScores, setSafetyScores] = useState<{ [key: string]: number }>({});
  const [exerciseName, setExerciseName] = useState('');
  const [selectedStudentForExercise, setSelectedStudentForExercise] = useState<string>('');
  const [selectedCompetencesForExercise, setSelectedCompetencesForExercise] = useState<string[]>([]);
  const [activeStudent, setActiveStudent] = useState<string | null>(null);

  const toast = useToast();
  const { isOpen: isReportOpen, onOpen: onReportOpen, onClose: onReportClose } = useDisclosure();
  const { isOpen: isSafetyOpen, onOpen: onSafetyOpen, onClose: onSafetyClose } = useDisclosure();
  const { isOpen: isExerciseOpen, onOpen: onExerciseOpen, onClose: onExerciseClose } = useDisclosure();

  const API_URL = process.env.REACT_APP_API_URL;

  const fetchSession = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/sessions/${id}`);
      const sessionData: Session = response.data;
      setSession(sessionData);
      if (sessionData.students.length > 0) {
        setActiveStudent(sessionData.students[0].name);
        const initialSafetyScores: { [key: string]: number } = {};
        sessionData.students.forEach(student => {
          initialSafetyScores[student.name] = 1;
        });
        setSafetyScores(initialSafetyScores);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error loading session',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  }, [id, toast, API_URL]);

  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  const createExercise = async () => {
    if (!exerciseName.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter an exercise name',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    if (!selectedStudentForExercise) {
      toast({
        title: 'Error',
        description: 'Please select a student for the exercise',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    if (selectedCompetencesForExercise.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one competence for the exercise',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      await axios.post(`${API_URL}/sessions/${id}/exercises/`, {
        name: exerciseName,
        student_name: selectedStudentForExercise,
        competences: selectedCompetencesForExercise,
      });

      setExerciseName('');
      setSelectedStudentForExercise('');
      setSelectedCompetencesForExercise([]);
      onExerciseClose();
      fetchSession();

      toast({
        title: 'Success',
        description: 'Exercise created successfully',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error creating exercise',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const toggleObservation = async (exerciseId: number, observationId: number, isChecked: boolean) => {
    try {
      await axios.put(`${API_URL}/exercises/${exerciseId}/observations/${observationId}`, {
        is_checked: isChecked
      });
      fetchSession();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error updating observation',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const completeExercise = async (exerciseId: number) => {
    try {
      await axios.put(`${API_URL}/exercises/${exerciseId}/complete`);
      fetchSession();
      toast({
        title: 'Success',
        description: 'Exercise completed',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error completing exercise',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleGenerateReport = async () => {
    try {
      const safetyScoresJson = JSON.stringify(safetyScores);
      const response = await axios.get(`${API_URL}/sessions/${id}/report/`, {
        params: {
          safety_scores: safetyScoresJson
        }
      });
      setReport(response.data);
      onReportOpen();
      onSafetyClose();
    } catch (error) {
      console.error("Error generating report:", error);
      toast({
        title: 'Error',
        description: 'Error generating report',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleGenerateReportClick = () => {
    onSafetyOpen();
  };

  const getGradeColor = (grade: number) => {
    switch (grade) {
      case 5: return 'green.500';  // Exemplary
      case 4: return 'blue.500';   // Effective
      case 3: return 'yellow.500'; // Adequate
      case 2: return 'orange.500'; // Minimum Acceptable
      case 1: return 'red.500';    // Ineffective
      default: return 'gray.500';
    }
  };

  const getGradeText = (grade: number) => {
    switch (grade) {
      case 5: return 'EXEMPLARY';
      case 4: return 'EFFECTIVE';
      case 3: return 'ADEQUATE';
      case 2: return 'MINIMUM ACCEPTABLE';
      case 1: return 'INEFFECTIVE';
      default: return 'UNKNOWN';
    }
  };

  const getHowManyText = (grade: number) => {
    switch (grade) {
      case 5: return 'All / Almost All';
      case 4: return 'Most';
      case 3: return 'Many';
      case 2: return 'Some';
      case 1: return 'Few / Hardly Any';
      default: return 'N/A';
    }
  };

  const getHowOftenText = (grade: number) => {
    switch (grade) {
      case 5: return 'Always / Almost Always';
      case 4: return 'Very Often';
      case 3: return 'Regularly';
      case 2: return 'Occasionally';
      case 1: return 'Rarely';
      default: return 'N/A';
    }
  };

  const getSafetyOutcomeText = (grade: number) => {
    switch (grade) {
      case 5: return 'Enhanced Safety';
      case 4: return 'Improved Safety';
      case 3: return 'Safe';
      case 2: return 'Minimum Acceptable Safety Level';
      case 1: return 'Unsafe';
      default: return 'N/A';
    }
  };

  const getRowBackgroundColor = (grade: number) => {
    switch (grade) {
      case 5: return 'green.100'; // Exemplary
      case 4: return 'green.50';  // Effective
      case 3: return 'yellow.50'; // Adequate
      case 2: return 'orange.50'; // Minimum Acceptable
      case 1: return 'red.50';    // Ineffective
      default: return 'white';
    }
  };

  if (!session) {
    return <Text>Loading...</Text>;
  }

  return (
    <>
      <VStack spacing={8} align="stretch">
        <Heading size="lg">Evaluation Session</Heading>
        
        <Box>
          <Text fontWeight="bold">Date:</Text>
          <Text>{new Date(session.date).toLocaleString()}</Text>
        </Box>

        <Box>
          <Text fontWeight="bold">Evaluated Students:</Text>
          <HStack spacing={2}>
            {session.students.map((student) => (
              <Badge
                key={student.name}
                colorScheme={activeStudent === student.name ? "purple" : "gray"}
                onClick={() => setActiveStudent(student.name)}
                cursor="pointer"
                px={3}
                py={1}
                borderRadius="md"
              >
                {student.name}
              </Badge>
            ))}
          </HStack>
        </Box>

        <HStack spacing={4}>
          <Button colorScheme="blue" onClick={onExerciseOpen}>
            New Exercise
          </Button>
          <Button colorScheme="green" onClick={handleGenerateReportClick}>
            Generate Report
          </Button>
        </HStack>

        <Divider />

        {activeStudent && (
          <Box>
            <Heading size="md" mb={4}>Exercises for {activeStudent}</Heading>
            {session.exercises
              .filter(exercise => exercise.observations.some(obs => obs.student_name === activeStudent))
              .map((exercise) => (
                <Box key={exercise.id} p={4} borderWidth="1px" borderRadius="lg" mb={4}>
                  <HStack justifyContent="space-between" alignItems="center" mb={4}>
                    <Heading size="sm">Exercise: {exercise.name} ({new Date(exercise.date).toLocaleString()})</Heading>
                    {!exercise.is_completed ? (
                      <Button size="sm" colorScheme="purple" onClick={() => completeExercise(exercise.id)}>
                        Complete Exercise
                      </Button>
                    ) : (
                      <Badge colorScheme="green">Completed</Badge>
                    )}
                  </HStack>
                  
                  <Table variant="simple">
                    <Thead>
                      <Tr>
                        <Th>Observed</Th>
                        <Th>Observation</Th>
                        <Th>OB Code</Th>
                        <Th>Competence</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {exercise.observations
                        .filter(obs => obs.student_name === activeStudent)
                        .map((observation) => (
                          <Tr key={observation.id}>
                            <Td>
                              <Checkbox
                                isChecked={observation.is_checked}
                                onChange={(e) => toggleObservation(exercise.id, observation.id, e.target.checked)}
                              />
                            </Td>
                            <Td>{observation.text}</Td>
                            <Td>{observation.ob_code}</Td>
                            <Td>{observation.competence}</Td>
                          </Tr>
                        ))}
                    </Tbody>
                  </Table>
                </Box>
              ))}

            {session.exercises.filter(exercise => exercise.observations.some(obs => obs.student_name === activeStudent)).length === 0 && (
              <Text>No exercises yet for {activeStudent}.</Text>
            )}
          </Box>
        )}

      </VStack>

      {/* New Exercise Modal */}
      <Modal isOpen={isExerciseOpen} onClose={onExerciseClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Create New Exercise</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl mb={4}>
              <FormLabel>Exercise Name</FormLabel>
              <Input
                placeholder="e.g., Takeoff, Landing, Emergency Procedure"
                value={exerciseName}
                onChange={(e) => setExerciseName(e.target.value)}
              />
            </FormControl>
            <FormControl mb={4}>
              <FormLabel>Select Student</FormLabel>
              <Select
                placeholder="Select student"
                value={selectedStudentForExercise}
                onChange={(e) => setSelectedStudentForExercise(e.target.value)}
              >
                {session.students.map((student) => (
                  <option key={student.name} value={student.name}>
                    {student.name}
                  </option>
                ))}
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>Competencies to Evaluate *</FormLabel>
              <CheckboxGroup
                colorScheme="blue"
                value={selectedCompetencesForExercise}
                onChange={(values) => setSelectedCompetencesForExercise(values as string[])}
              >
                <Stack spacing={2}>
                  {COMPETENCES.map((competence) => (
                    <Checkbox key={competence} value={competence}>
                      {competence}
                    </Checkbox>
                  ))}
                </Stack>
              </CheckboxGroup>
              <FormHelperText>Select at least one competence for this exercise</FormHelperText>
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" onClick={createExercise}>Create</Button>
            <Button variant="ghost" onClick={onExerciseClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Safety Score Modal */}
      <Modal isOpen={isSafetyOpen} onClose={onSafetyClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Enter Safety Scores</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              {session.students.map(student => (
                <FormControl key={student.name}>
                  <FormLabel>Safety Score for {student.name} (1-5)</FormLabel>
                  <NumberInput
                    defaultValue={safetyScores[student.name]}
                    min={1}
                    max={5}
                    onChange={(_, valueAsNumber) => setSafetyScores(prev => ({ ...prev, [student.name]: valueAsNumber }))}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
              ))}
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="green" onClick={handleGenerateReport}>Generate Report</Button>
            <Button variant="ghost" onClick={onSafetyClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Report Modal */}
      <Modal isOpen={isReportOpen} onClose={onReportClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Evaluation Report</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {report && Object.keys(report).length > 0 ? (
              <VStack spacing={8} align="stretch">
                {Object.entries(report).map(([studentName, studentReport]) => (
                  <Box key={studentName}>
                    <Heading size="md" mb={4}>Report for {studentName}</Heading>
                    <Box display="flex" justifyContent="center">
                      <Table variant="simple" size="sm" borderWidth="1px" borderColor="gray.200" width="fit-content" margin="0 auto">
                        <Thead>
                          <Tr>
                            <Th rowSpan={2} textAlign="left" bg="blue.700" color="white" borderRightWidth="1px" borderColor="gray.200">COMPETENCE</Th>
                            <Th colSpan={2} textAlign="center" bg="blue.700" color="white" borderRightWidth="1px" borderColor="gray.200">REQUIRED OBSERVABLE BEHAVIOURS</Th>
                            <Th rowSpan={2} textAlign="center" bg="blue.700" color="white" borderRightWidth="1px" borderColor="gray.200">TEM SAFETY OUTCOME?</Th>
                            <Th rowSpan={2} textAlign="right" bg="blue.700" color="white">GRADE & LEVEL OF COMPETENCE</Th>
                          </Tr>
                          <Tr>
                              <Th textAlign="center" bg="blue.700" color="white" borderRightWidth="1px" borderColor="gray.200">HOW MANY?</Th>
                              <Th textAlign="center" bg="blue.700" color="white" borderRightWidth="1px" borderColor="gray.200">HOW OFTEN?</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {studentReport.report && Object.entries(studentReport.report).map(([competence, scores]) => {
                            if (
                              typeof scores === 'object' &&
                              scores !== null &&
                              'how_many' in scores &&
                              'how_often' in scores &&
                              'safety_score' in scores &&
                              'final_grade' in scores
                            ) {
                              return (
                                <Tr key={competence} borderBottomWidth="1px" borderColor="gray.200" bg={getRowBackgroundColor(scores.final_grade)}>
                                  <Td fontWeight="bold" borderRightWidth="1px" borderColor="gray.200" textAlign="left">
                                    {competence}
                                  </Td>
                                  <Td textAlign="center" borderRightWidth="1px" borderColor="gray.200">
                                    <Text fontSize="md" fontWeight="bold">{scores.how_many}</Text> ({getHowManyText(scores.how_many)})
                                  </Td>
                                  <Td textAlign="center" borderRightWidth="1px" borderColor="gray.200">
                                    <Text fontSize="md" fontWeight="bold">{scores.how_often}</Text> ({getHowOftenText(scores.how_often)})
                                  </Td>
                                  <Td textAlign="center" borderRightWidth="1px" borderColor="gray.200">
                                    <Text fontSize="md" fontWeight="bold">{scores.safety_score}</Text> ({getSafetyOutcomeText(scores.safety_score)})
                                  </Td>
                                  <Td textAlign="center">
                                    <Text color={getGradeColor(scores.final_grade)} fontWeight="bold" fontSize="lg">
                                      {scores.final_grade} ({getGradeText(scores.final_grade)})
                                    </Text>
                                  </Td>
                                </Tr>
                              );
                            }
                            return null;
                          })}
                        </Tbody>
                      </Table>
                    </Box>
                    {/* Section for unchecked observations */}
                    {studentReport.unchecked_observations && studentReport.unchecked_observations.length > 0 && (
                      <Box mt={6} textAlign="center">
                        <Text fontWeight="bold" mb={2} color="red.600">Observations Not Observed :</Text>
                        <VStack align="center" spacing={1}>
                          {studentReport.unchecked_observations.map((obs, idx) => (
                            <Text key={idx} fontSize="sm">
                              <b>{obs.competence}</b> - {obs.ob_code}: {obs.text}
                            </Text>
                          ))}
                        </VStack>
                      </Box>
                    )}
                  </Box>
                ))}
              </VStack>
            ) : (
              <Text>No report generated yet.</Text>
            )}
          </ModalBody>
          <ModalFooter>
            <Button onClick={onReportClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default SessionView; 