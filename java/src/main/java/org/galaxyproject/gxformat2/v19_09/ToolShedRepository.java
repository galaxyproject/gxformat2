// Copyright Common Workflow Language project contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Saveable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository</I><br>
 * This interface is implemented by {@link ToolShedRepositoryImpl}<br>
 */
public interface ToolShedRepository extends Saveable {
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/name</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The name of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  String getName();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/changeset_revision</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * The revision of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  String getChangeset_revision();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/owner</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The owner of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  String getOwner();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/tool_shed</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The URI of the tool shed containing the repository this tool can be found in - typically this
   * should be toolshed.g2.bx.psu.edu. *
   *
   * </BLOCKQUOTE>
   */
  String getTool_shed();
}
