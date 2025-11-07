// frontend/src/test/SubgraphApiTest.tsx
// Composant de test pour vérifier l'IntelliSense et la validation des types

import React from 'react'
import apiService from '@/services/api'
import type { SubgraphCreatePayload } from '@/types/api'

/**
 * Ce composant sert uniquement à tester l'IntelliSense et la validation TypeScript.
 * 
 * TESTS À EFFECTUER DANS VOTRE ÉDITEUR :
 * 
 * 1. IntelliSense - Tapez "apiService." ci-dessous et vérifiez que vous voyez :
 *    - createSubgraph
 *    - getSubgraph
 *    - updateSubgraph
 *    - deleteSubgraph
 *    - assignNodesToSubgraph
 *    - unassignNodesFromSubgraph
 * 
 * 2. Validation des types - Décommentez l'exemple d'erreur ci-dessous.
 *    TypeScript devrait signaler une erreur car le champ 'subproject_id' est manquant.
 */
export const SubgraphApiTest: React.FC = () => {
  
  // ✅ EXEMPLE CORRECT : Tous les champs requis sont présents
  const testCorrectPayload = async () => {
    const validPayload: SubgraphCreatePayload = {
      subproject_id: 1,
      title: "Mon Cluster",
      style_class_ref: "styleA",
      node_ids: [1, 2, 3]
    }
    
    try {
      const result = await apiService.createSubgraph(validPayload)
      console.log('Subgraph créé:', result)
    } catch (error) {
      console.error('Erreur:', error)
    }
  }

  // ❌ EXEMPLE D'ERREUR : Décommentez pour tester la validation TypeScript
  // TypeScript devrait signaler une erreur car 'subproject_id' est manquant
  /*
  const testInvalidPayload = async () => {
    const invalidPayload: SubgraphCreatePayload = {
      // subproject_id: 1,  // ⚠️ MANQUANT - TypeScript doit signaler une erreur
      title: "Mon Cluster",
      node_ids: [1, 2, 3]
    }
    
    await apiService.createSubgraph(invalidPayload)
  }
  */

  // TEST D'INTELLISENSE : Tapez "apiService." ci-dessous et vérifiez l'autocomplétion
  const testIntelliSense = async () => {
    // Tapez "apiService." ici pour voir toutes les méthodes disponibles ↓
    // apiService.
    
    // Exemples d'utilisation :
    await apiService.getSubgraph(1)
    await apiService.updateSubgraph(1, { title: "Nouveau titre", style_class_ref: null })
    await apiService.assignNodesToSubgraph(1, [4, 5, 6])
    await apiService.unassignNodesFromSubgraph(1, [4])
    await apiService.deleteSubgraph(1)
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>Test des API Subgraphs</h2>
      <p>Ce composant sert à tester l'IntelliSense dans VSCode.</p>
      <button onClick={testCorrectPayload}>
        Tester createSubgraph (payload valide)
      </button>
      <button onClick={testIntelliSense} style={{ marginLeft: '10px' }}>
        Tester toutes les méthodes
      </button>
    </div>
  )
}

export default SubgraphApiTest
